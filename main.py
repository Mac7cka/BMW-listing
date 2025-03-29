from scraper import *
from email_handler import send_email_with_attachment
from utils import load_dotenv, save_to_excel, handle_consent
from config import *
import os
import time
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

# Email credentials
FROM_EMAIL = os.getenv("FROM_EMAIL")   # Replace with your email
MY_PASSWORD = os.getenv("MY_PASSWORD")    # Replace with your email password or app-specific password
TO_EMAIL = os.getenv("TO_EMAIL")       # Replace with your email


def main():
    driver = setup_driver()

    url = (
        f"{URL}cars?price_from={MIN_PRICE}&price_to={MAX_PRICE}&year_from={MIN_YEAR}&year_to={MAX_YEAR}&make={BRAND}"
        f"&model:{MODELS[0]},{MODELS[1]}&sort=publishdatedesc")

    driver.get(url)
    handle_consent(driver)

    deals = scrape_data(driver, not_suitable_locations)
    print(f"Total deals found: {len(deals)}")

    with open("deals.json", "w") as file:
        json.dump(deals, file, indent=4)

    # Save to Excel and get file path
    file_path = save_to_excel(deals)

    # Send email only if file exists
    if file_path:
        send_email_with_attachment(deals, file_path)
    else:
        print("No deals found, skipping email.")

    time.sleep(3)
    driver.quit()


if __name__ == "__main__":
    main()