from selenium.webdriver.support import expected_conditions as EC

import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import os
import logging
import pandas as pd
from openpyxl import load_workbook
import datetime

LOADING_TIME = 2


def load_dotenv():
    """ Load environment variables from a .env file. """
    from dotenv import load_dotenv
    if not os.path.exists(".env"):
        logging.error("No .env file found.")
        return
    load_dotenv()


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
