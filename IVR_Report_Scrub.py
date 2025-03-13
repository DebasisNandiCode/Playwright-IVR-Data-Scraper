import os
import shutil  # Import shutil to move across different drives
import pandas as pd
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import asyncio
import nest_asyncio
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from Logger import Logger
from dotenv import load_dotenv
from Send_Emails import SendEmails  # Import the class correctly

# Load environment variables from .env file
load_dotenv()

# Initialize Logger
logger = Logger()

# Use SendEmails class
send_email = SendEmails.send_email  # Aassign the function
# send_email = SendEmails()  # FIX: Create an instance of the class

# Use environment variables instead of hardcoded values
WEBSITE_URL = os.getenv("WEBSITE_URL")
WEBSITE_USERNAME = os.getenv("WEBSITE_USERNAME")
WEBSITE_PASSWORD = os.getenv("WEBSITE_PASSWORD")

USERNAME_XPATH = os.getenv("USERNAME_XPATH")
PASSWORD_XPATH = os.getenv("PASSWORD_XPATH")
LOGIN_BUTTON_XPATH = os.getenv("LOGIN_BUTTON_XPATH")

REPORT_URL = os.getenv("REPORT_URL")
DROPDOWN_IFRAME_XPATH = os.getenv("DROPDOWN_IFRAME_XPATH")
DROPDOWN_OPTIONS_XPATH = os.getenv("DROPDOWN_OPTIONS_XPATH")
FILTER_BUTTON_XPATH = os.getenv("FILTER_BUTTON_XPATH")
DOWNLOAD_BUTTON_XPATH = os.getenv("DOWNLOAD_BUTTON_XPATH")

# Get database credentials
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Properly encode password for SQLAlchemy
encoded_password = quote_plus(DB_PASSWORD)


# Get the directory where the script is located
base_Dir = os.path.dirname(os.path.abspath('~'))

# Initialize date variables
today_date = datetime.now()
previous_date = today_date - timedelta(days=1)
folder_date = previous_date.strftime('%Y%m%d')
# start_date = previous_date.strftime('%Y/%m/%d') + " 00:00"
# end_date = previous_date.strftime('%Y/%m/%d') + " 23:59"

# Define the raw data folder
rawFile_Dir = os.path.join(base_Dir, 'Raw_Files')
rawDateFile_Dir = os.path.join(rawFile_Dir, folder_date)

if not os.path.exists(rawDateFile_Dir):
    os.makedirs(rawDateFile_Dir)

# Print output for verification
print(f"Raw File Directory: {rawDateFile_Dir}")

# Insert data into the database
def insert_data_to_db(file_path):
    try:
        df = pd.read_csv(file_path)

        row_count = df.dropna(how="all").shape[0]
        print(f"Total number of non-empty rows: {row_count}")

        column_count = df.shape[1]
        print(f"Total number of columns: {column_count}")

        if df.empty:
            logger.log_to_database(287, "Info", "IVR Data", "Success", 
                                "IVR Dataframe is empty", "Success", "Dataframe Empty")
            send_email("Info! IVR Dataframe is Empty", "There is no data into IVR Dataframe today")
            print("IVR Dataframe is empty. Skipping Insertion of data")
        else:
            column_rename_cols = {
                'Date' : 'Date',
                'CLI' : 'CLI',
                'DNIS' : 'DNIS',
                'Location' : 'Location',
                'CUCID' : 'CUCID',
                'ApplicationIVR' : 'ApplicationIVR',
                'Hour' : 'Hour',
                'IVRStartTime' : 'IVRStartTime',
                'IVREndTime' : 'IVREndTime',
                'IVRDuration' : 'IVRDuration',
                'IVR Billing Category' : 'IVR_Billing_Category',
                'QueVDN' : 'QueVDN',
                'Level' : 'Level',
                'QueDuration' : 'QueDuration',
                'QueStartTime' : 'QueStartTime',
                'QueEndTime' : 'QueEndTime',
                'AgentID' : 'AgentID',
                'AgentStartTime' : 'AgentStartTime',
                'AgentEndTime' : 'AgentEndTime',
                'AgentDuration' : 'AgentDuration',
                'ansholdtime' : 'ansholdtime',
                'Agent Dispose' : 'Agent_Dispose',
                'Total Time at agent' : 'Total_Time_at_agent',
                'Agent Billing Category' : 'Agent_Billing_Category',
                'TotalDuration' : 'TotalDuration',
                'Traversal' : 'Traversal',
                'FRL' : 'FRL',
                'transferred' : 'transferred',
                'disconnectedBy' : 'disconnectedBy'
            }

            rename_map = column_rename_cols.copy()
            df.rename(columns={col: rename_map[col] for col in df.columns if col in rename_map}, inplace=True)

            engine = create_engine(f"mssql+pyodbc://{DB_USER}:{encoded_password}@{DB_HOST}/{DB_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server")

            df.to_sql('ivrReport_DB', con=engine, if_exists='append', index=False)

            logger.log_to_database(287, "Success", "IVR Data", "Success",
                                   f"IVR {df.shape[0]} Data Successfully inserted into DB",
                                   "Success", "Data Inserted")
            send_email("Success! IVR Data Process Completed",f"IVR Rows: {row_count} & Columns: {column_count} Data has been successfully downloaded and {df.shape[0]} Data inserted into the database")
            print("IVR Data Successfully inserted into DB")

    except Exception as e:
            logger.log_to_database(287, "Warning", "IVR Data", "Failed",
                                   "Failed to insert IVR Data into DB",
                                   "Error", "Data Failed")
            send_email("Failed! IVR Data insertion failed into DB", f"Database Insertion Error: {e}")
            print("IVR Data Failed to insert into DB")

# Define data scrubbing process
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        # Set browser timezone to IST
        context = await browser.new_context(
            accept_downloads=True, 
            timezone_id="Asia/Kolkata"  # Set Time Zone to IST
        )

        page = await context.new_page()
        await page.goto(WEBSITE_URL)
        await asyncio.sleep(2)

        # Login
        try:
            await page.fill(USERNAME_XPATH, WEBSITE_USERNAME)
            await asyncio.sleep(2)
            await page.fill(PASSWORD_XPATH, WEBSITE_PASSWORD)
            await asyncio.sleep(2)
            await page.click(LOGIN_BUTTON_XPATH)
            await asyncio.sleep(2)

            logger.log_to_database(287, "Info", "IVR Data", "Success",
                                   "Login Successfully into portal for IVR Data",
                                   "Success", "Login")
            
            print("Login successful!")
            await asyncio.sleep(3)

        except Exception as e:
            logger.log_to_database(287, "Warning", "IVR Data", "Failed",
                                   "Login Failed into portal for IVR Data",
                                   "Error", "Login Failed")
            send_email("Failed! Login Failed into portal", f"Login Error: {e}")
            await browser.close()
            return
        
        # Navigate to report page and interact with dropdowns
        try:
            await page.goto(REPORT_URL)
            await asyncio.sleep(5)

            ### **Switch to the iframe FIRST before interacting with the dropdown**
            iframe_element = await page.wait_for_selector("//iframe", timeout=10000)
            iframe = await iframe_element.content_frame()

            if iframe is None:
                raise Exception("Failed to locate the iframe!")

            # **Click the dropdown inside the iframe**
            dropdown = await iframe.wait_for_selector(DROPDOWN_IFRAME_XPATH, timeout=10000)
            await dropdown.click()
            await asyncio.sleep(2)  # Allow dropdown options to load

            # **Select the 3rd option from the dropdown (which should be "Yesterday")**
            dropdown_options = await iframe.query_selector_all(DROPDOWN_OPTIONS_XPATH)
            
            if len(dropdown_options) >= 3:
                await dropdown_options[2].click()  # Selecting the 3rd option (index 2)
                await asyncio.sleep(2)  # Wait after selection
            else:
                raise Exception("Dropdown options not found or less than 3")

            # **Click Apply Button**
            apply_button = await iframe.wait_for_selector(FILTER_BUTTON_XPATH, timeout=10000)
            await apply_button.click()
            await asyncio.sleep(5)

            # **Click Download Button and Wait for Download to Finish**
            async with page.expect_download() as download_info:  # FIX: Use `page.expect_download()`
                download_button = await iframe.wait_for_selector(DOWNLOAD_BUTTON_XPATH, timeout=50000)
                await download_button.click()

            # Wait for the file to download
            download = await download_info.value
            download_path = await download.path()

            if download_path:
                # Move the file to the desired location
                final_path = os.path.join(rawDateFile_Dir, download.suggested_filename)

                shutil.move(download_path, final_path)  # FIX: Use shutil.move() to move across different drives
                print(f"Download Completed: {final_path}")

                # send_email("Success! Downloaded IVR Data Successfully", f"Downloaded IVR Data successfully from portal\nFile saved at: {final_path}")
                logger.log_to_database(287, "Info", "IVR Data", "Success",
                                   "Downloaded IVR Data Successfully from portal",
                                   "Success", "Data Downloaded")
            else:
                raise Exception("Download failed - No file path found")

        except Exception as e:
            logger.log_to_database(287, "Warning", "IVR Data", "Failed",
                                   "Download Failed IVR Data from portal",
                                   "Error", "Download Failed")
            send_email("Failed! Download IVR Data from portal", f"Download Error: {e}")

        await browser.close()

        insert_data_to_db(final_path)


# Run the script
if __name__ == "__main__":
    nest_asyncio.apply()  # Enables nested event loops
    asyncio.run(main())
