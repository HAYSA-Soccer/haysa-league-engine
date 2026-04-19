import os, json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config.settings import SHEET_ID

def get_sheets_service():
    info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds)

def write_df(df, sheet_range):
    service = get_sheets_service()
    values = [df.columns.tolist()] + df.astype(str).fillna("").values.tolist()
    service.spreadsheets().values().clear(
        spreadsheetId=SHEET_ID,
        range=sheet_range,
    ).execute()
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=sheet_range.split("!")[0] + "!A1",
        valueInputOption="RAW",
        body={"values": values},
    ).execute()
