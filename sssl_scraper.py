import pandas as pd
import requests
from bs4 import BeautifulSoup
from sheets_writer import write_df
from config.settings import SSSL_SCHEDULE_RANGE, SHEET_ID
from googleapiclient.discovery import build
from sheets_writer import get_sheets_service

def get_sssl_contests():
    service = get_sheets_service()
    resp = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range="SSSL_Contests!A2:C"
    ).execute()
    rows = resp.get("values", [])
    return [{"division_code": r[0], "url": r[1]} for r in rows if len(r) >= 2]

def scrape_sssl_contest(url, division_code) -> pd.DataFrame:
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    # TODO: parse the SSSL table into a DataFrame
    # Must include: Date, Time, Home, Away, Location, Score, Division_Code
    raise NotImplementedError

def main():
    contests = get_sssl_contests()
    frames = []
    for c in contests:
        df = scrape_sssl_contest(c["url"], c["division_code"])
        frames.append(df)
    if frames:
        all_df = pd.concat(frames, ignore_index=True)
        write_df(all_df, SSSL_SCHEDULE_RANGE)

if __name__ == "__main__":
    main()
