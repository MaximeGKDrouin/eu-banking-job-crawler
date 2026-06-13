import logging
import requests
from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper
from datetime import datetime

logger = logging.getLogger("FinanceScraper.Portals")

class WorkdayAtsScraper(BaseScraper):
    """
    Scrapes banks using Workday (e.g., Morgan Stanley, Bank of America).
    Targets the /wday/cxs/ internal API.
    """
    def scrape(self) -> List[Dict[str, Any]]:
        listings = []
        offset = 0
        limit = 20
        has_more = True

        while has_more:
            payload = {
                "appliedFacets": {},
                "limit": limit,
                "offset": offset,
                "searchText": ""
            }
            try:
                logger.info(f"[{self.name}] Fetching Workday API offset {offset}...")
                response = requests.post(self.base_url, json=payload, headers=self._get_headers(), timeout=15)
                response.raise_for_status()
                data = response.json()
                
                job_postings = data.get("jobPostings", [])
                if not job_postings:
                    break
                    
                for job in job_postings:
                    listings.append({
                        "bank_name": self.name,
                        "title": job.get("title", ""),
                        "location": job.get("locationsText", ""),
                        "contract_type": job.get("timeType", "Unknown"),
                        # Workday rarely exposes deadlines in the search API, requires detail fetch
                        "application_deadline": None, 
                        "start_date": None,
                        "url": f"{self.base_url.split('/wday')[0]}{job.get('externalPath', '')}"
                    })
                
                offset += limit
                # Prevent infinite loops during testing; in production, you can let it run
 
            except Exception as e:
                logger.error(f"Failed parsing Workday API for {self.name}: {str(e)}")
                break
                
        return listings

class OracleHcmScraper(BaseScraper):
    """
    Scrapes banks using Oracle Cloud HCM (e.g., Goldman Sachs, JPMorgan).
    Targets the /hcmRestApi/resources/latest/recruitingCEJobRequisitions API.
    """
    def scrape(self) -> List[Dict[str, Any]]:
        listings = []
        offset = 0
        limit = 25
        has_more = True

        while has_more:
            # Oracle HCM requires fetching a specific payload structure
            payload = {
                "findCriteria": {
                    "filter": "",
                    "limit": limit,
                    "offset": offset
                }
            }
            
            headers = self._get_headers()
            headers["Content-Type"] = "application/vnd.oracle.adf.resourceitem+json;charset=utf-8"

            try:
                logger.info(f"[{self.name}] Fetching Oracle HCM API offset {offset}...")
                response = requests.post(
                    f"{self.base_url}?onlyData=true&expand=all", 
                    json=payload, 
                    headers=headers, 
                    timeout=15
                )
                response.raise_for_status()
                data = response.json()
                
                items = data.get("items", [])
                if not items:
                    break
                    
                for item in items:
                    job = item.get("requisitionList", [{}])[0] if item.get("requisitionList") else item
                    
                    # Convert Oracle date strings to datetime objects
                    posted_date_str = job.get("PostedDate")
                    deadline_dt = datetime.strptime(posted_date_str[:10], "%Y-%m-%d") if posted_date_str else None

                    listings.append({
                        "bank_name": self.name,
                        "title": job.get("Title", ""),
                        "location": job.get("PrimaryLocation", ""),
                        "contract_type": job.get("JobSchedule", "Unknown"),
                        "application_deadline": deadline_dt, # Using posted date as a fallback proxy for filter logic
                        "start_date": None,
                        "url": f"{self.base_url.split('/hcmRestApi')[0]}/hcmUI/CandidateExperience/en/sites/CX/job/{job.get('Id')}"
                    })

                has_more = data.get("hasMore", False)
                offset += limit
                
            except Exception as e:
                logger.error(f"Failed parsing Oracle HCM API for {self.name}: {str(e)}")
                break
                
        return listings