import requests
from bs4 import BeautifulSoup
import pandas as pd 
import gspread
from google.oauth2.service_account import Credentials


# Step 1: Get the 2024/25 season page
base_url = 'https://fbref.com'
url = f'{base_url}/en/comps/9/history/Premier-League-Seasons'

season_link = None

# Define the scope for Google Sheets API
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
]

# Load your service account credentials from the JSON key file
creds = Credentials.from_service_account_file('C:\\Users\DELL\\Downloads\\web-scrapping-459314-df2c304f4f11.json', scopes=scope)
gc = gspread.authorize(creds)
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1WYv25vpTL38W_x3VjlVY_PdnraoMessYdc-zJmJrroU/edit?gid=0#gid=0'
try:
    spreadsheet = gc.open_by_url(spreadsheet_url)
    worksheet = spreadsheet.sheet1
    print(f"Spreadsheet opened successfully using URL: {spreadsheet.title}")
except gspread.SpreadsheetNotFound:
    print(f"Error: Spreadsheet not found at URL: {spreadsheet_url}")
    exit()
except Exception as e:
    print(f"An error occurred while opening by URL: {e}")
    exit()

#function to scrape the table with single headers
def scrape_single_header_table(soup, table_id, sheet_title, spreadsheet):
    """
    Scrapes a table with a single-row header structure using the previously working code.
    """
    try:
        worksheet = spreadsheet.worksheet(sheet_title)
        print(f"Opened existing worksheet: {sheet_title}")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_title, rows=100, cols=20)
        print(f"Created new worksheet: {sheet_title}")
    except Exception as e:
        print(f"Error accessing/creating worksheet '{sheet_title}': {e}")
        return

    table = soup.find('table', id=table_id)
    if not table:
        print(f"Table with id '{table_id}' not found.")
        return

    table_data = []
    thead = table.find('thead')
    if thead:
        all_headers = thead.find_all('th')
        headers = [th.text for th in all_headers] # Include all headers
        if headers and headers[0] == '':
            headers = headers[1:] # Remove the first empty header if present
        print(f"Number of headers found: {len(headers)}")
        table_data.append(headers)
    else:
        print("<thead> not found in the table.")

    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
        print(f"Number of rows found in tbody: {len(rows)}")
        for row in rows:
            row_data = []
            # Find the row header (rank)
            rank_cell = row.find('th', scope="row")
            if rank_cell:
                row_data.append(rank_cell.text)
            # Find all the data cells
            data_cells = row.find_all('td')
            for cell in data_cells:
                row_data.append(cell.text)

            print(f"Number of data elements in row: {len(row_data)}")
            print(f"Data in row: {row_data}")

            if len(row_data) == len(headers) and row_data:
                table_data.append(row_data)
            elif row_data:
                print(f"Warning: Row has {len(row_data)} columns, expected {len(headers)}")
    else:
        print("<tbody> not found in the table.")

    if table_data and len(table_data) > 1: # Ensure there's header and at least one data row
        df_table = pd.DataFrame(table_data[1:], columns=table_data[0])
        print("\nExtracted Table Data:")
        print(df_table)

        # Write the table DataFrame to the new worksheet
        worksheet.clear()
        worksheet.update([df_table.columns.values.tolist()] + df_table.values.tolist())
        print(f"Table data successfully written to '{sheet_title}'!")

    else:
        print("No data to write to the 'Premier League' sheet.")


  
    
#function to scrape the table with grouped headers
def scrape_grouped_header_table(soup, table_id, sheet_title, spreadsheet):
    """Scrapes a table with a two-row grouped header structure.

    Args:
        soup (_type_): _description_
        table_id (_string_): _description_
        sheet_title (_string_): _description_
        gc (_type_): _description_
        spreadsheet (_type_): _description_
    """
    try:
        # Try to access or create the worksheet
        try:
            worksheet = spreadsheet.add_worksheet(title=sheet_title, rows=100, cols=20)
            print(f"Created new worksheet: {sheet_title}")
        except Exception:
            worksheet = spreadsheet.worksheet(sheet_title)
            print(f"Opened existing worksheet: {sheet_title}")

        table = soup.find('table', id=table_id)
        if not table:
            print(f"Table with id '{table_id}' not found.")
            return

        thead = table.find('thead')
        headers = []

        if thead:
            header_rows = thead.find_all('tr')
            if len(header_rows) >= 2:
                top_row = header_rows[0].find_all('th')
                bottom_row = header_rows[1].find_all('th')

                # Assume first few bottom headers are without a top group
                headers.extend([th.text.strip() for th in bottom_row[:4]])

                top_row_index = 1
                bottom_row_index = 4

                while bottom_row_index < len(bottom_row):
                    top_header = top_row[top_row_index].text.strip()
                    colspan = int(top_row[top_row_index].get('colspan', 1))
                    for _ in range(colspan):
                        if bottom_row_index < len(bottom_row):
                            headers.append(f"{top_header} - {bottom_row[bottom_row_index].text.strip()}")
                            bottom_row_index += 1
                    top_row_index += 1
            elif header_rows:
                headers = [th.text.strip() for th in header_rows[0].find_all('th')]
            else:
                print("No header rows found.")
                return
        else:
            print("No <thead> found.")
            return

        # Parse <tbody>
        tbody = table.find('tbody')
        table_data = []
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                row_data = []
                rank_cell = row.find('th', scope="row")
                if rank_cell:
                    row_data.append(rank_cell.text.strip())
                row_data += [td.text.strip() for td in row.find_all('td')]

                if row_data:
                    table_data.append(row_data)
        else:
            print("No <tbody> found.")
            return

        if table_data and len(headers) == len(table_data[0]):
            df = pd.DataFrame(table_data, columns=headers)
            worksheet.clear()
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            print(f"Successfully wrote data to '{sheet_title}'")
        else:
            print(f"Header/Data column mismatch or empty data in '{sheet_title}'")
    except Exception as e:
        print(f"Error in scraping table '{table_id}': {e}")
        
        
# --- Main Scraping Logic ---
base_url = 'https://fbref.com'
url = f'{base_url}/en/comps/9/history/Premier-League-Seasons'

try:
    response = requests.get(url)
    response.raise_for_status()
    soup_season_history = BeautifulSoup(response.content, 'html.parser')

    link_element = soup_season_history.find('a', string='2024-2025')
    if link_element:
        season_link = base_url + link_element.get('href')
        print(f"Found 2024-2025 season link: {season_link}")

        response_season = requests.get(season_link)
        response_season.raise_for_status()
        soup_season = BeautifulSoup(response_season.content, 'html.parser')

        tables_to_scrape = [
            {'id': 'results2024-202591_overall', 'title': 'Premier League', 'header_type': 'single'},
            {'id': 'stats_squads_standard_for', 'title': 'Squad Standard Stats', 'header_type': 'grouped'},
            {'id': 'stats_squads_possession_for', 'title': 'Squad Possession', 'header_type': 'grouped'},
            {'id': 'stats_squads_playing_time_for', 'title': 'Squad Playing Time', 'header_type': 'grouped'},
            {'id': 'stats_squads_misc_for', 'title': 'Squad Miscellaneous Stats', 'header_type': 'grouped'}
            # Add header_type for all your tables
        ]
        for table_info in tables_to_scrape:
            if table_info['header_type'] == 'single':
                scrape_single_header_table(soup_season, table_info['id'], table_info['title'], spreadsheet)
            elif table_info['header_type'] == 'grouped':
                scrape_grouped_header_table(soup_season, table_info['id'], table_info['title'], spreadsheet)
            else:
                print(f"Unknown header type '{table_info['header_type']}' for table '{table_info['id']}'.")
    else:
        print("Link with text '2024-2025' not found.")

except requests.exceptions.RequestException as e:
    print(f"Error fetching the webpage: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
    
