# Premier League Web Scraper to Google Sheets

This project scrapes multiple statistics tables from the 2024/25 Premier League season page on [FBRef](https://fbref.com) and uploads the cleaned data into separate worksheets in a connected Google Spreadsheet.

## Features

- Automatically finds and navigates to the 2024/25 Premier League season page.
- Extracts general metadata (e.g., competition, number of teams) from the page.
- Dynamically extracts tables by their `id` attribute, even if the table has a double header (multi-level `<thead>`).
- Automatically creates or opens the appropriate Google Sheets worksheets and uploads the scraped data.
- Reusable scraping function for any other similar table on the same page.

## Prerequisite
Before running the script, ensure you have the following:

* **Python 3.6 or higher:**
 Install them using pip:
    ```bash
    pip install -r requirements.txt

    ```
* **Google Sheets API Credentials:**
    1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
    2.  Create a new project or select an existing one.
    3.  Enable the **Google Sheets API** and **Google Drive API**.
    4.  Create a service account and download the JSON credentials file.
    5.  **Share your Google Sheet** with the email address of the service account (found in the JSON key file). Give it "Editor" access.

## Setup
1.  **Clone or download** this repository/script.
2.  **Install the required Python libraries** as mentioned in the Prerequisites.
3.  **Download your Google Sheets API credentials JSON file** and place it in the same directory as the script (or update the path in the `creds` variable).
4.  **Update the `spreadsheet_url` variable** in the script with the URL of your Google Sheet.
