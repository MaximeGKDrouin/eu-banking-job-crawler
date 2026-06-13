import os
import sys
import logging
import time
import pandas as pd
import schedule
from datetime import datetime
from config import config
from pipeline.filters import JobFilterEngine
from scrapers.portal_scrapers import OracleHcmScraper, WorkdayAtsScraper, DynamicJSScraper

# Setup Comprehensive Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("scraper_pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("FinanceScraper.Orchestrator")

def run_pipeline():
    logger.info("Initializing Scraping Execution Cycle...")
    filter_engine = JobFilterEngine()
    aggregated_raw_data = []

    # Initialize Active Scraper Registry
# Initialize Active Scraper Registry
    scrapers = [
        # --- ORACLE HCM BANKS ---
        OracleHcmScraper(
            name="Goldman Sachs", 
            base_url="https://hdpc.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?siteNumber=CX_1"
        ),
        OracleHcmScraper(
            name="JPMorgan", 
            base_url="https://jpmc.fa.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?siteNumber=CX_1001"
        ),
        
        # --- WORKDAY ATS BANKS ---
        WorkdayAtsScraper(
            name="Morgan Stanley", 
            base_url="https://morganstanley.wd1.myworkdayjobs.com/wday/cxs/morganstanley/morganstanley/jobs"
        ),
        WorkdayAtsScraper(
            name="Piper Sandler", 
            # This is the actual hidden JSON endpoint, not the frontend HTML site
            base_url="https://pipersandler.wd1.myworkdayjobs.com/wday/cxs/pipersandler/Piper_Sandler_Careers/jobs"
        ),

        # --- NON-STANDARD ATS BANKS (Lincoln International, Lazard, etc.) ---
        # For banks that do not use Workday or Oracle, you must use the Playwright UI scraper
        # we designed in the first step, as they do not expose a standardized JSON API.
        DynamicJSScraper(
            name="Lincoln International",
            base_url="https://www.lincolninternational.com/careers/"
        )
    ]
    for bank_name, url in config.BANK_PORTALS.items():
        # Assign appropriate scraper classes depending on known gateway types
        scrapers.append(WorkdayAtsScraper(name=bank_name, base_url=url))
    
    # Run parsing workflows
    # Run parsing workflows
    for scraper in scrapers:
        try:
            logger.info(f"Initiating scraping sequence for {scraper.name}...")
            raw_results = scraper.scrape()
            
            if raw_results:
                logger.info(f"Successfully scraped {len(raw_results)} raw jobs from {scraper.name}.")
                aggregated_raw_data.extend(raw_results)
            else:
                logger.warning(f"No jobs found or returned from {scraper.name}.")
                
        except Exception as e:
            logger.error(f"Critical execution error tracking {scraper.name}: {str(e)}")

    # Execute downstream filtration sequence
    final_processed_jobs = []
    for raw_job in aggregated_raw_data:
        processed = filter_engine.process_and_filter(raw_job)
        if processed:
            final_processed_jobs.append(processed)

    if not final_processed_jobs:
        logger.warning("Pipeline completed successfully, but zero items matched criteria.")
        return

    # Export Sequence
    df = pd.DataFrame(final_processed_jobs)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    csv_path = os.path.join(config.OUTPUT_DIR, "scraped_jobs.csv")
    excel_path = os.path.join(config.OUTPUT_DIR, "scraped_jobs.xlsx")
    
    df.to_csv(csv_path, index=False)
    df.to_excel(excel_path, index=False, engine='openpyxl')
    logger.info(f"Data persistently saved to {csv_path} and {excel_path}")

    # Generate Terminal Matrix Summaries
    print("\n" + "="*50)
    print("           JOB SCRAPING PROCESSING METRICS       ")
    print("="*50)
    print("\n--- Total Matches Found Per Bank ---")
    print(df["Bank Name"].value_counts().to_string())
    print("\n--- Total Matches Found Per Target Destination ---")
    print(df["Location"].value_counts().to_string())
    print("="*50 + "\n")

def start_scheduler():
    logger.info("Scheduler daemon actively started. Running sequence every 24 hours.")
    schedule.every().day.at("01:00").do(run_pipeline) # Run past midnight to maximize capture rate
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        start_scheduler()
    else:
        run_pipeline()