import gspread
from gspread import Worksheet
from google.oauth2.service_account import Credentials

import os
import dotenv
import pandas as pd

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


def get_sheets_id(sheet_link: str) -> str:
    """
    Extracts the ID of a Google Sheets document from its URL.
    :param sheet_link: The URL of the Google Sheets document.
    :return: The ID of the Google Sheets document.
    """
    return sheet_link.split('/')[-2]


def get_sheet_by_id(sheet_id: str):
    """
    Fetches a Google Sheets document by its ID.
    :param sheet_id: The ID of the Google Sheets document.
    :return: The Google Sheets document.
    """
    return client.open_by_key(sheet_id)


def get_sheets_info(sheets_links: list[str]) -> dict:
    """
    Extracts the ID and title of Google Sheets documents from their URLs.
    :param sheets_links: A list of URLs of Google Sheets documents.
    :return: A dictionary where the key is the title of the document and the value is the ID.
    """
    sheets_info = {}
    for og_link in sheets_links:
        clear_link = og_link.strip()
        try:
            sheet_id = get_sheets_id(clear_link)
            sheet = client.open_by_key(sheet_id)
        except Exception as e:
            print(f"Failed to open the document by link: {og_link}")
            print(f"Exception: {e}")
            continue
        sheets_info[sheet.title] = sheet_id
    return sheets_info


def get_all_worksheets(sheet_id: str) -> list[Worksheet]:
    """
    Fetches all worksheets from a Google Sheets document.
    :param sheet_id: The ID of the Google Sheets document.
    :return: A list of all worksheets in the document.
    To see the titles of the worksheet, use .title attribute.
    """
    sheet = client.open_by_key(sheet_id)
    worksheets = sheet.worksheets()
    return worksheets


def get_all_worksheets_list(sheet_id: str) -> list[str]:
    """
    Fetches all worksheets from a Google Sheets document.
    :param sheet_id: The ID of the Google Sheets document.
    :return: A list of all worksheets in the document.
    """
    sheet = client.open_by_key(sheet_id)
    worksheets = sheet.worksheets()
    return [ws.title for ws in worksheets]


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


def get_header_id(worksheet: Worksheet, header: str) -> int:
    """
    Fetches the headers of a worksheet and returns a dictionary with the header names as keys
    and their column indexes as values.

    :param worksheet: The worksheet object.
    :return: A dictionary where the key is the header name and the value is the column index.
    """
    column_id = None
    # Find the column index of the unit column if not provided
    all_data = worksheet.get_all_values()
    headers_row = all_data[0]
    for i in range(len(headers_row)):
        if headers_row[i].lower() == header.lower():
            column_id = i
            break

    if column_id is None:
        raise Exception(f"Header {header} not found in the worksheet.")
    return column_id


def worksheet_to_dataframe(worksheet: Worksheet, header_row: int = 1) -> pd.DataFrame:
    """
    Converts a worksheet to a pandas DataFrame and adds a simulated ID column.
    :param worksheet: The worksheet object.
    :param header_row: The row number that contains the headers.
    :return: A pandas DataFrame with an extra 'ID_simulated' column.
    """
    # Fetch all data from the worksheet
    all_data = worksheet.get_all_values()

    # Extract header and data
    header = all_data[header_row - 1]
    data = all_data[header_row:]

    # Create DataFrame
    df = pd.DataFrame(data, columns=header)

    # Add the 'ID_simulated' column
    df['ID_simulated'] = range(1, len(df) + 1)

    return df


def fetch_lesson_videos_info(unit_df: pd.DataFrame, lesson_name: str) -> dict:
    """
    Fetches the information about the videos in a lesson.
    :param unit_df:
    :param lesson_name:
    :return: dict with video_id as key and video info as value
    """

    lessons_df = unit_df[unit_df['Lesson'] == lesson_name]

    info = {}
    for i, row in lessons_df.iterrows():
        status = row['Status']
        video_title = row['Title']
        video_link = row['Link']
        actor = row['Actor']
        video_id = row['ID_simulated']

        info[video_id] = {
            'status': status,
            'video_title': video_title,
            'video_link': video_link,
            'actor': actor,
        }

    return info


if __name__ == "__main__":
    # Test the functions
    sheets_info = get_sheets_info(SHEETS_LINKS)  # {'FOR TESTING': ..., 'FOR TESTING - копія': ...}
    print(SHEETS_LINKS)
    sheet = get_sheet_by_id(sheets_info['FOR TESTING'])
    worksheets = get_all_worksheets(sheet.id)
    worksheet = get_worksheet(sheet.id, worksheets[0].title)
    dataframe = worksheet_to_dataframe(worksheet)

    unit_df = dataframe[dataframe['Unit'] == 'Unit 1: Polynomial arithmetic']
    lesson_name = 'Intro to polynomials'
    info = fetch_lesson_videos_info(unit_df, lesson_name)
    print(info)
