import pandas as pd
from datetime import datetime
from sheets_writer import get_sheets_service, write_df
from config.settings import SHEET_ID, TS_SCHEDULE_RANGE, SSSL_SCHEDULE_RANGE, MAPPING_RANGE, COMPARISON_RANGE

def read_range(range_name):
    service = get_sheets_service()
    resp = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=range_name
    ).execute()
    rows = resp.get("values", [])
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows[1:], columns=rows[0])

def main():
    today = datetime.now().date()

    ts_df = read_range(TS_SCHEDULE_RANGE)
    sssl_df = read_range(SSSL_SCHEDULE_RANGE)
    mapping_df = read_range(MAPPING_RANGE)

    # normalize dates
    for df in (ts_df, sssl_df):
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

    ts_past = ts_df[ts_df["Date"] < today].copy()
    sssl_past = sssl_df[sssl_df["Date"] < today].copy()

    # TODO: join using mapping_df (TS team ↔ SSSL team/division)
    # and build a comparison DataFrame with:
    # - Missing TS score
    # - Missing SSSL score
    # - Score mismatch
    # - Schedule mismatch
    comparison = pd.DataFrame()  # placeholder

    write_df(comparison, COMPARISON_RANGE)

if __name__ == "__main__":
    main()
