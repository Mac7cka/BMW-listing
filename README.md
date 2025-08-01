# Car Deals Scraper

## 📜 Description


A Python-based scraper designed to extract car deal information from websites, save the data to an Excel file, and send it via email. 
The script uses Selenium for web scraping and offers a streamlined approach to finding deals based on user-specified criteria such as car brand, model, price range, year range, and location preferences.


---


## 🛠️ Features


- **Automated Web Scraping: Utilizes Selenium to fetch car deal information.**  

Data Extraction: Retrieves details such as:

* Car title

* Location

* Year

* Fuel type

* Mileage

* Posting time

Pagination Handling: Collects data across multiple pages until all deals are scraped.

Excel Export: Saves the scraped information to an Excel file with dynamic column width adjustments for easy viewing.

Email Notification: Sends the data via email with the Excel file as an attachment.


---


## ⚙️ Requirements

## Python Packages:

The following Python libraries are required:

* selenium

* pandas

* openpyxl

* python-dotenv

* pip install selenium pandas openpyxl python-dotenv


---


## System Requirements:
Chrome browser installed.

ChromeDriver compatible with your Chrome version.

## 📝 Setup Instructions

## Dependencies

- Selenium
- pandas
- openpyxl
- python-dotenv
- re
- smtplib
- dotenv (to load environment variables)
- pip install -r requirements.txt
- Configure .env File: 
  Create a .env file in the project directory and add your email credentials as shown above.

## Environment Variables

The following environment variables should be set in a `.env` file:

- `FROM_EMAIL`: Your email address (sender)
- `MY_PASSWORD`: Your email password (or app-specific password)
- `TO_EMAIL`: The recipient's email address



## Usage

Run the Script:
To run the script, simply run: 

### python main.py


Update the following constants in the script if necessary, but make sure it fits website criteria:

BRAND: Car brand name (e.g., "BMW").

MODELS: List of car models to search (e.g., ["3-Series", "5-Series"]).

MIN_YEAR and MAX_YEAR: Year range for the search.

MIN_PRICE and MAX_PRICE: Price range for the search.

not_suitable_locations: List of unsuitable locations to filter out.

Run the script:
The scraped data will be saved as an Excel file and emailed to the recipient.


## 🛑 Error Handling

The script includes error handling for:

The script automatically handles consent popups on the DoneDeal website by clicking the "Agree" button

Missing elements

Unsuitable locations

New posts

Errors such as missing attachments or unsuccessful email notifications will be logged.


## 🔒 Notes

Ensure the .env file is properly set up with valid credentials to avoid authentication issues.

Regularly update ChromeDriver to match your browser version for compatibility.

## Known Issues and Future Improvements

- The script might encounter issues if the website structure changes.
#   B M W - l i s t i n g 
 
 
