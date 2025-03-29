from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.common.exceptions import NoSuchElementException
import re
from utils import is_location_suitable, handle_consent, click_on_next_btn_pagination


def setup_driver():
    """ Initialize and return a Chrome WebDriver instance. """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=chrome_options)


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
