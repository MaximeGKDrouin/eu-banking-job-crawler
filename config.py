import os
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict

class ScraperConfig(BaseModel):
    # Target Constraints
    TARGET_LOCATIONS: List[str] = ["london", "paris"]
    TARGET_DIVISIONS: List[str] = ["investment banking", "asset management", "financial markets"]
    
    # 2027 Availability Window
    WINDOW_START: datetime = datetime(2027, 3, 1)
    WINDOW_END: datetime = datetime(2027, 8, 31)
    
    # Scraping Parameters
    CRAWL_DELAY: float = 2.0  # Seconds between requests per domain
    MAX_RETRIES: int = 3
    OUTPUT_DIR: str = "output"
    
    # Unified Mapping for Target Institutions and official career page references
    # NOTE: Credit Suisse operations have been integrated into UBS; monitored under the UBS workflow.
    BANK_PORTALS: Dict[str, str] = {
        "Goldman Sachs": "https://www.goldmansachs.com/careers/",
        "Morgan Stanley": "https://www.morganstanley.com/careers",
        "JPMorgan": "https://careers.jpmorgan.com/",
        "Bank of America": "https://careers.bankofamerica.com/",
        "Barclays": "https://search.jobs.barclays/",
        "Deutsche Bank": "https://careers.db.com/",
        "UBS": "https://www.ubs.com/global/en/careers.html",
        "Citigroup": "https://careers.citigroup.com/",
        "HSBC": "https://www.hsbc.com/careers",
        "Jefferies": "https://www.jefferies.com/careers/",
        "Houlihan Lokey": "https://hl.com/careers/",
        "Lazard": "https://www.lazard.com/careers/",
        "Rothschild": "https://www.rothschildandco.com/en/careers/",
        "Evercore": "https://www.evercore.com/careers/",
        "Moelis": "https://www.moelis.com/careers/",
        "William Blair": "https://www.williamblair.com/Careers.aspx",
        "Baird": "https://www.rwbaird.com/careers/",
        "Piper Sandler": "https://www.pipersandler.com/careers",
        "Lincoln International": "https://www.lincolninternational.com/careers/"
    }
    
    AGGREGATORS: Dict[str, str] = {
        "LinkedIn": "https://www.linkedin.com/jobs",
        "Indeed": "https://www.indeed.com",
        "WelcomeToTheJungle": "https://www.welcometothejungle.com",
        "eFinancialCareers": "https://www.efinancialcareers.com"
    }

config = ScraperConfig()

# Terms of Service (ToS) Compliance Register:
# - LinkedIn & Indeed explicitly prohibit automated scraping within their Robots.txt / ToS without explicit written consent.
# - eFinancialCareers employs Cloudflare protection to mitigate programmatic traffic.
# - Ensure corporate execution aligns with local data access laws and specific institutional permissions.