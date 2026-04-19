import time
import pandas as pd
from io import StringIO
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from sheets_writer import write_df
from config.settings import TS_SCHEDULE_RANGE

BASE_URL = "https://www.haysa.org/schedules"

# -------------------------
# Driver
# -------------------------
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=chrome_options)

# -------------------------
# Scraping helpers
# -------------------------
def get_schedule_links(driver):
    driver.get(BASE_URL)

    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.XPATH, '//*[@id="SchedulesPageLayout"]//a'))
    )

    links = driver.find_elements(By.XPATH, '//*[@id="SchedulesPageLayout"]//a')

    schedule_links = []
    for link in links:
        href = link.get_attribute("href")
        text = link.text.strip()
        if href and "/schedule/" in href.lower():
            schedule_links.append({"url": href, "division": text})

    return schedule_links

def extract_schedule_table(driver):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[@id='ctl00_ContentPlaceHolder1_StandingsResultsControl_ScheduleGrid_ctl00']")
        )
    )
    table_element = driver.find_element(
        By.XPATH, "//*[@id='ctl00_ContentPlaceHolder1_StandingsResultsControl_ScheduleGrid_ctl00']"
    )
    table_html = driver.execute_script("return arguments[0].outerHTML;", table_element)
    df = pd.read_html(StringIO(table_html))[0]
    df.columns = ["Date", "Time", "Home", "Away", "Location"]
    return df

def clean_schedule_df(df, division):
    # Remove header rows like "Date" or "Time"
    valid_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    df = df[df["Date"].astype(str).str[:3].isin(valid_days)]

    # Extract scores from Home/Away
    def extract_number(text):
        text = str(text).strip()
        match = re.search(r"(\d+)$", text)
        if match:
            return text[:text.rfind(match.group())].strip(), int(match.group())
        return text.strip(), None

    df["HomeScore"] = df["Home"].apply(lambda x: extract_number(x)[1])
    df["Home"] = df["Home"].apply(lambda x: extract_number(x)[0])

    df["AwayScore"] = df["Away"].apply(lambda x: extract_number(x)[1])
    df["Away"] = df["Away"].apply(lambda x: extract_number(x)[0])

    df["Division"] = division

    return df

def extract_schedule_data(url, driver, division):
    driver.get(url)
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    df = extract_schedule_table(driver)
    df = clean_schedule_df(df, division)
    return df

# -------------------------
# MAIN
# -------------------------
def main():
    driver = setup_driver()
    links = get_schedule_links(driver)

    all_frames = []
    for link in links:
        df = extract_schedule_data(link["url"], driver, link["division"])
        if df is not None and not df.empty:
            all_frames.append(df)

    driver.quit()

    if not all_frames:
        print("No TS data found.")
        return

    ts_df = pd.concat(all_frames, ignore_index=True)

    # Write to Google Sheets
    write_df(ts_df, TS_SCHEDULE_RANGE)

if __name__ == "__main__":
    main()
