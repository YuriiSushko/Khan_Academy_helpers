import gspread
from google.oauth2.service_account import Credentials

import os
import dotenv


# Load environment variables
dotenv.load_dotenv()

SHEETS_LINKS_STR = os.getenv('SHEETS_LINKS')
SHEETS_LINKS = SHEETS_LINKS_STR.split(',')

# Load credentials and create a client
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
]

creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)

client = gspread.authorize(creds)


def get_sheet_id(sheet_link: str) -> str:
    """
    Extracts the ID of a Google Sheets document from its URL.
    :param sheet_link: The URL of the Google Sheets document.
    :return: The ID of the Google Sheets document.
    """
    return sheet_link.split('/')[-2]


def get_sheets_info(sheets_links: list) -> dict:
    """
    Extracts the ID and title of Google Sheets documents from their URLs.
    :param sheets_links: A list of URLs of Google Sheets documents.
    :return: A dictionary where the key is the title of the document and the value is the ID.
    """
    sheets_info = {}
    for link in sheets_links:
        try:
            sheet_id = get_sheet_id(link)
            sheet = client.open_by_key(sheet_id)
        except Exception as e:
            print(f"Failed to open the document by link: {link}")
            print(f"Exception: {e}")
            continue
        sheets_info[sheet.title] = link
    return sheets_info


def get_all_worksheets(sheet_id: str) -> list:
    """
    Fetches all worksheets from a Google Sheets document.
    :param sheet_id: The ID of the Google Sheets document.
    :return: A list of all worksheets in the document.
    To see the titles of the worksheet, use .title attribute.
    """
    sheet = client.open_by_key(sheet_id)
    worksheets = sheet.worksheets()
    return worksheets


def get_worksheet(sheet_id: str, worksheet_name: str):
    """
    Fetches a specific worksheet from a Google Sheets document.
    :param sheet_id: The ID of the Google Sheets document.
    :param worksheet_name: The title of the worksheet.
    :return: Worksheet: The worksheet object.
    """
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)
    return worksheet


def parse_data_by_units(all_data: list, unit_column_id: int = 2) -> dict:
    """
    Parses the data and returns a dict with unit numbers as keys
    and lists of tuples (row number, row data) as values.

    :param all_data: The list of rows from the worksheet.
    :param unit_column_id: The index of the column that contains the unit information.
    :return: A dictionary where the key is the unit number and the value is a list of tuples (row number, row data).
    """

    parsed_data = {}

    # Find the column index of the unit column if not provided
    if unit_column_id == -1:
        header_row = all_data[0]
        for i in range(len(header_row)):
            if header_row[i].lower() == 'unit':
                unit_column_id = i
                break

    # Iterate over rows and organize them by unit number
    for i, row in enumerate(all_data[1:], start=1):  # Skip the header row, row numbers start from 2
        unit = row[unit_column_id]

        if not unit:  # Skip rows with no unit
            continue

        if unit not in parsed_data:
            parsed_data[unit] = []
        parsed_data[unit].append((i, row))  # Store the row number along with the row data

    return parsed_data


if __name__ == "__main__":
    # Fetch all worksheets and display their titles
    print(SHEETS_LINKS)
    info = get_sheets_info(SHEETS_LINKS)
    print(info)
    SHEET_ID = get_sheet_id(SHEETS_LINKS[0])
    worksheets = get_all_worksheets(SHEET_ID)
    print("Available worksheets:")
    for i, ws in enumerate(worksheets):
        print(f"{i + 1}. {ws.title}")

    # Let the user select a worksheet by its number
    selected_index = int(input("Enter the number of the worksheet you want to fetch: ")) - 1
    selected_worksheet = worksheets[selected_index].title

    # Fetch the selected worksheet
    worksheet = get_worksheet(SHEET_ID, selected_worksheet)

    # Example: Fetch all values from the selected worksheet
    data = worksheet.get_all_values()

    # Example: Parse the data by units
    data_dict = parse_data_by_units(data, -1)
    print("Parsed data:")
    print(data_dict.keys())

    print(data_dict['Unit 12: Modeling'])
