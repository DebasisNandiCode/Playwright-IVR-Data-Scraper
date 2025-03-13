# Playwright-IVR-Data-Scraper
# Overview

This Python script automates the process of logging into the portal, downloading the IVR data report, processing the data, and inserting it into a Microsoft SQL Server database. It also includes logging and email notifications for success or failure events.

# Features

Automated login to portal using Playwright.

Selecting yesterday's report via dropdown in an iframe.

Downloading the report and saving it in a date-based folder.

Processing the CSV data and inserting it into a Microsoft SQL Server database.

Sending email notifications for success or failure events.

Logging all activities into the database.

# Prerequisites

Required Python Packages

Ensure you have the required Python packages installed:

pip install pandas playwright sqlalchemy pyodbc python-dotenv nest_asyncio

# Environment Variables

Create a .env file in the project directory and define the following environment variables:

WEBSITE_URL=<login URL>
WEBSITE_USERNAME=<Your username>
WEBSITE_PASSWORD=<Your password>

USERNAME_XPATH=<XPath for username field>
PASSWORD_XPATH=<XPath for password field>
LOGIN_BUTTON_XPATH=<XPath for login button>

REPORT_URL=<Report page URL>
DROPDOWN_IFRAME_XPATH=<XPath for dropdown iframe>
DROPDOWN_OPTIONS_XPATH=<XPath for dropdown options>
FILTER_BUTTON_XPATH=<XPath for filter button>
DOWNLOAD_BUTTON_XPATH=<XPath for download button>

DB_HOST=<Database host>
DB_DATABASE=<Database name>
DB_USER=<Database username>
DB_PASSWORD=<Database password>

# Folder Structure

The script automatically creates a Raw_Files directory inside the base directory, organizing reports into subfolders named by date (YYYYMMDD format).

Project_Root/
│-- main.py
│-- .env
│-- Logger.py
│-- Send_Emails.py
│-- Raw_Files/
    ├── 20250312/
    ├── 20250313/

# How It Works

Login to the portal - Uses Playwright to enter credentials and navigate to the reports page.

Apply filter - Selects yesterday's report from the dropdown and applies filters.

Download report - Waits for the file to download and moves it to the appropriate directory.

Process CSV Data - Reads the CSV, renames columns, and inserts data into a Microsoft SQL Server database.

Logging & Notifications - Logs all activities and sends email notifications based on success or failure.

Running the Script

python main.py

Error Handling

Logs all events into the database.

Sends failure notifications if login, download, or database insertion fails.

# Author

Developed by Debasis Nandi
