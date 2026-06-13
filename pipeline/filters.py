import re
from datetime import datetime
from typing import Dict, Any, Optional
from config import config

class JobFilterEngine:
    def __init__(self):
        self.location_patterns = [re.compile(rf"\b{loc}\b", re.IGNORECASE) for loc in config.TARGET_LOCATIONS]
        self.division_patterns = {
            "Investment Banking": re.compile(r"investment\s+banking|m\&a|corporate\s+finance|advisory", re.IGNORECASE),
            "Asset Management": re.compile(r"asset\s+management|wealth\s+management|investment\s+management", re.IGNORECASE),
            "Financial Markets": re.compile(r"sales\s+\&\s+trading|financial\s+markets|quantitative|structuring|equity\s+research", re.IGNORECASE)
        }

    def match_location(self, location_text: str) -> Optional[str]:
        if not location_text:
            return None
        for loc in config.TARGET_LOCATIONS:
            if re.search(rf"\b{loc}\b", location_text.lower(), re.IGNORECASE):
                return loc.capitalize()
        return None

    def match_division(self, title: str, description: str = "") -> Optional[str]:
        combined_text = f"{title} {description}"
        for div_name, pattern in self.division_patterns.items():
            if pattern.search(combined_text):
                return div_name
        return None

    def verify_temporal_window(self, title: str, start_dt: Optional[datetime]) -> bool:
        """
        Validates if target positions match the 2027 target window heuristically.
        """
        title_lower = title.lower()
        
        # Heuristic 1: Explicit mention of the target year
        if "2027" in title_lower:
            return True
            
        # Heuristic 2: Entry-level/Intern roles posted currently (2026) are for 2027 cycles
        entry_keywords = ["intern", "summer analyst", "graduate", "off-cycle", "vie", "apprenticeship"]
        if any(kw in title_lower for kw in entry_keywords):
            return True
            
        # Heuristic 3: Strict start date validation if the ATS actually provided one
        if start_dt:
            return config.WINDOW_START <= start_dt <= config.WINDOW_END
            
        return False

    def process_and_filter(self, raw_job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        loc = self.match_location(raw_job.get("location", ""))
        if not loc:
            return None

        title = raw_job.get("title", "")
        div = self.match_division(title, raw_job.get("description", ""))
        if not div:
            return None

        # Filter out senior requirements
        invalid_experience_keywords = ["vp", "vice president", "associate director", "senior manager", "3+", "5+ years", "director"]
        if any(kw in title.lower() for kw in invalid_experience_keywords):
            return None

        # Apply the new heuristic temporal window check
        start_dt = raw_job.get("start_date")
        if not self.verify_temporal_window(title, start_dt):
            return None

        return {
            "Bank Name": raw_job.get("bank_name"),
            "Role Title": title,
            "Division": div,
            "Location": loc,
            "Contract Type": raw_job.get("contract_type", "Internship/Graduate"),
            "Application Deadline": raw_job.get("application_deadline").strftime('%Y-%m-%d') if raw_job.get("application_deadline") else "Unlisted",
            "Start Date": start_dt.strftime('%Y-%m-%d') if start_dt else "2027 Window",
            "Direct Application URL": raw_job.get("url")
        }