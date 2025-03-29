import smtplib
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import pandas as pd
import os
import json
import re
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from openpyxl import load_workbook
from dotenv import load_dotenv
from email.message import EmailMessage

# Setup logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

# Email credentials
FROM_EMAIL = os.getenv("FROM_EMAIL")   # Replace with your email
MY_PASSWORD = os.getenv("MY_PASSWORD")    # Replace with your email password or app-specific password
TO_EMAIL = os.getenv("TO_EMAIL")       # Replace with your email


# Constants
LOADING_TIME = 2
URL = "https://www.donedeal.ie/"

BRAND = "BMW"
MODELS = ["3-Series", "5-Series"]
MIN_YEAR = 2009
MAX_YEAR = 2025
MIN_PRICE = 3000
MAX_PRICE = 6000

not_suitable_locations = [
    "Co. Antrim", "Co. Armagh", "Co. Derry", "Co. Down", "Co. Fermanagh", "Co. Tyrone"
]


def setup_driver():
    """ Initialize and return a Chrome WebDriver instance. """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=chrome_options)


def handle_consent(driver):
    """ Handle cookie consent pop-up. """
    try:
        accept_btn = driver.find_element(by=By.ID, value='didomi-notice-agree-button')
        accept_btn.click()
        time.sleep(LOADING_TIME)
    except NoSuchElementException:
        pass


def click_on_next_btn_pagination(driver):
    """ Click the 'Next' button to load more data. """
    try:
        next_btn = driver.find_element(By.XPATH,
                                       '//*[@id="__next"]/div[1]/div[5]/div/div/div[2]/div[2]/div/div/span[3]/button')
        next_btn.click()
        time.sleep(LOADING_TIME)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Listingsstyled__List-sc-1iabgue-0.fXuet"))
        )
    except NoSuchElementException:
        pass


def is_location_suitable(location, not_suitable_locations):
    """ Check if the location is not in the unsuitable locations list."""
    for unsuitable_location in not_suitable_locations:
        if unsuitable_location in location:
            return False
    return True


def has_new_posts(driver, processed_links):
    """ Check if the current page contains any posts from today. """
    containers = driver.find_elements(By.CLASS_NAME, "Listingsstyled__List-sc-1iabgue-0.fXuet")
    for container in containers:
        lis = container.find_elements(By.TAG_NAME, 'li')
        for li in lis:
            try:
                link = li.find_element(By.TAG_NAME, 'a').get_attribute("href")
                if "?campaign=" in link:
                    continue
                if link not in processed_links:
                    whole_text = li.text
                    if re.search(r'(\d+)\s*hour', whole_text):
                        return True # Found a new post, continue scraping
            except NoSuchElementException:
                continue
    return False


def extract_deals_data(driver, not_suitable_locations, processed_links):
    """ Extracts data about car deals from the page and filters unsuitable locations """
    deals = []
    containers = driver.find_elements(By.CLASS_NAME, "Listingsstyled__List-sc-1iabgue-0.fXuet")
    for container in containers:
        try:
            lis = container.find_elements(By.TAG_NAME, 'li')
            for li in lis:

                try:
                    link = li.find_element(By.TAG_NAME, 'a').get_attribute("href")
                    # Skip spotlighted posts
                    if "?campaign=" in link or link in processed_links:
                        continue
                except NoSuchElementException:
                    continue
                # Extract link
                try:
                    link = li.find_element(By.TAG_NAME, 'a').get_attribute("href")
                    if link in processed_links:
                        continue
                except NoSuchElementException:
                    link = "N/A"
                    continue

                # Extract title
                try:
                    title = li.find_element(By.TAG_NAME, 'p').text
                except NoSuchElementException:
                    title = "N/A"

                # Extract date added
                whole_text = li.text
                hours_match = re.search(r'(\d+)\s*hour', whole_text)
                if not hours_match:
                    continue # Skip if not added today
                hours_before = int(hours_match.group(1))

                # Extract mileage
                mileage = "N/A"
                mileage_match = re.search(r'(\d+,\d+)\s*km', whole_text)
                if mileage_match:
                    mileage = mileage_match.group(1)

                # Extract year, fuel type, location
                year, fuel_type, location = "N/A", "N/A", "N/A"
                info_match = re.search(r'(\d{4})\s*(\d\.\d\s*[a-zA-Z]*)\s*([\d,]+ km).'
                                       r'*(?:\d+\s*hour[s]*)?\s*([a-zA-Z,]+\s*Co.\s*[a-zA-Z]*)', whole_text)
                if info_match:
                    year = info_match.group(1)
                    fuel_type = info_match.group(2)
                    location = info_match.group(4)
                else:
                    try:
                        meta_info_items = li.find_elements(By.CLASS_NAME,
                                                           'SearchCardV2styled__MetaInfoItem-sc-1s58fbn-8')
                        if len(meta_info_items) >= 5:
                            year = meta_info_items[0].text
                            fuel_type = meta_info_items[1].text
                            location = meta_info_items[4].text
                            mileage = meta_info_items[2].text

                        elif len(meta_info_items) >= 4:
                            year = meta_info_items[0].text
                            fuel_type = meta_info_items[1].text
                            location = meta_info_items[3].text
                            mileage = meta_info_items[2].text

                    except NoSuchElementException:
                        pass

                # Check location suitability
                if not is_location_suitable(location, not_suitable_locations):
                    continue

                if title and link and location and fuel_type != "N/A":
                    deal = {
                        "title": title,
                        "location": location,
                        "year": year,
                        "fuel_type": fuel_type,
                        "mileage": mileage,
                        "hours_before": hours_before,
                        "link": link,
                    }
                    print(deal)
                    deals.append(deal)
                    processed_links.add(link)

        except NoSuchElementException:
            continue
    return deals


def scrape_data(driver, not_suitable_locations):
    """ Main function to scrape car deals while handling pagination. """
    all_deals = []
    processed_links = set()
    while True:
        current_page_deals = extract_deals_data(driver, not_suitable_locations, processed_links)
        all_deals.extend(current_page_deals)

        if not has_new_posts(driver, processed_links):
            print("No new posts found.")
            break

        click_on_next_btn_pagination(driver)
    return all_deals


def save_to_excel(deals):
    """ Save the scraped car deals data to an Excel file with adjusted column widths and return file path. """
    if not deals:
        print("No deals found, skipping file save.")
        return None  # Return None if there are no deals

    # Get today's date for filename
    today = datetime.datetime.now().strftime("%d_%m_%Y")
    file_path = f"car_deals_{today}.xlsx"

    # Convert deals to DataFrame
    df = pd.DataFrame(deals)
    df.to_excel(file_path, index=False)

    # Adjust column widths using openpyxl
    wb = load_workbook(file_path)
    ws = wb.active
    for col in ws.columns:
        max_length = max((len(str(cell.value)) if cell.value else 0) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max_length + 2  # Add padding

    # Save adjusted file
    wb.save(file_path)

    print(f"✅ Saved {len(deals)} deals to {file_path}")

    return file_path  # Return the file path for email attachment


def send_email_with_attachment(deals, TO_EMAIL, attachment_path):
    """ Sends an email with a list of car deals in the body and an Excel file attachment. """
    today = datetime.datetime.now().strftime("%d.%m.%Y")

    if not deals:
        logging.warning("No deals found, skipping email.")
        return

    subject = f"🔥 New Car Deals - {today}"
    body = "Here are the latest car deals:\n\n"
    for deal in deals:
        body += (f"🚗 {deal['title']}\n📍 Location: {deal['location']}\n📅 Year: {deal['year']}\n⛽ "
                 f"Fuel: {deal['fuel_type']}\n🔗 Link: {deal['link']}\n\n")

    msg = EmailMessage()
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    msg.set_content(body)

    if os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as attachment:
                file_data = attachment.read()
                file_name = os.path.basename(attachment_path)
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
        except Exception as e:
            logging.error(f"Error attaching file: {e}")
            return
    else:
        logging.warning(f"Attachment file {attachment_path} not found. Sending email without attachment.")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(FROM_EMAIL, MY_PASSWORD)
            server.send_message(msg)
        logging.info(f"✅ Email sent successfully to {TO_EMAIL}")
    except Exception as e:
        logging.error(f"❌ Failed to send email: {e}")


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
        send_email_with_attachment(deals, TO_EMAIL, file_path)
    else:
        print("No deals found, skipping email.")

    time.sleep(3)
    driver.quit()


if __name__ == "__main__":
    main()


