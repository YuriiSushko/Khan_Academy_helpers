import gspread
from google.oauth2.service_account import Credentials
import os
import dotenv
import json


# Load environment variables
dotenv.load_dotenv()

SHEET_ID = os.getenv('SHEET_ID')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
]

creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)

client = gspread.authorize(creds)

sheet_id = '1eWcxih5YqlGpkqf2MWcqf_fdzLrHReIsW3H0K3PgVZw'

sheet = client.open_by_key(sheet_id)

worksheets = sheet.worksheets()
print(worksheets)
