import scrape_reviews
import cluster_reviews
import generate_pulse
import send_weekly_pulse
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    logging.info("Starting Weekly Product Pulse Pipeline...")

    # Step 1: Scrape Reviews
    logging.info("Step 1: Scraping Reviews...")
    if not scrape_reviews.run():
        logging.error("Step 1 Failed: Scraping reviews failed. Aborting.")
        sys.exit(1)
    logging.info("Step 1 Complete.")

    # Step 2: Cluster Reviews
    logging.info("Step 2: Clustering Reviews...")
    if not cluster_reviews.run():
        logging.error("Step 2 Failed: Clustering reviews failed. Aborting.")
        sys.exit(1)
    logging.info("Step 2 Complete.")

    # Step 3: Generate Pulse Report
    logging.info("Step 3: Generating Pulse Report...")
    if not generate_pulse.run():
        logging.error("Step 3 Failed: Generating pulse report failed. Aborting.")
        sys.exit(1)
    logging.info("Step 3 Complete.")

    # Step 4: Send Email
    logging.info("Step 4: Sending Weekly Email...")
    if not send_weekly_pulse.run():
        logging.error("Step 4 Failed: Sending email failed. Aborting.")
        sys.exit(1)
    logging.info("Step 4 Complete.")

    logging.info("Pipeline Completed Successfully.")

if __name__ == "__main__":
    main()
