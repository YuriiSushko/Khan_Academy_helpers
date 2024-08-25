import pandas as pd
from datetime import datetime

# Replace with your Google Sheet URL
SHEET_URL = {'Arithmetic': 'https://docs.google.com/spreadsheets/d/1Si5f329_SYqas2s0ELLK817b-WU6iOgMkGCw4WMki9g/export?format=csv',
             'Precalculus': 'https://docs.google.com/spreadsheets/d/1czPUsPANW7a4ZX4nTfuyl1J53wGwyiP7Jqtwta_zjkM/export?format=csv',
             'Algebra 2': '',
             'Basic geometry and measurements': ''
}


def get_google_sheets_data(course):
    # Fetch the Google Sheet as a DataFrame
    df = pd.read_csv(SHEET_URL[course])
    return df


def get_all_entries(name, surname, course):
    # Get data from Google Sheets
    df = get_google_sheets_data(course)

    if df.empty:
        return []

    # Join name and surname with a space and handle case sensitivity
    full_name_1 = (name + " " + surname).strip().lower()
    full_name_2 = (surname + " " + name).strip().lower()

    # Ensure 'Actor' column is in lowercase
    df['Actor'] = df['Actor'].str.strip().str.lower()

    # Filter rows where the 'Actor' matches the constructed full names
    filtered_df = df[(df['Actor'] == full_name_1) | (df['Actor'] == full_name_2)]

    if filtered_df.empty:
        print("No matching records found.")
        return []

    # Convert the 'Timestamp' column to datetime objects using .loc to avoid SettingWithCopyWarning
    filtered_df.loc[:, 'Timestamp'] = pd.to_datetime(filtered_df['Timestamp'], format='%Y-%m-%d %H:%M:%S')

    # Sort the filtered DataFrame by 'Timestamp' in descending order (most recent first)
    sorted_df = filtered_df.sort_values(by='Timestamp', ascending=False)

    # Return all matching rows as a list of dictionaries
    return sorted_df.to_dict(orient='records')
