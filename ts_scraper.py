import pandas as pd
from datetime import datetime
from sheets_writer import write_df
from config.settings import TS_SCHEDULE_RANGE

def scrape_ts_schedule() -> pd.DataFrame:
    # TODO: paste your existing Selenium scraping logic here
    # Return a DataFrame with at least:
    # Date, Time, Home, Away, Location, Score, Division, TS_Team_ID, TS_Team_Name
    raise NotImplementedError

def main():
    df = scrape_ts_schedule()
    # filter out future games if you want TS_Schedule to be “all games” or “all + future”
    write_df(df, TS_SCHEDULE_RANGE)

if __name__ == "__main__":
    main()
