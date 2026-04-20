import pandas as pd
from io import StringIO
from playwright.sync_api import sync_playwright
from sheets_writer import write_df
from config.settings import TS_SCHEDULE_RANGE

BASE_URL = "https://www.haysa.org/schedules"

def get_schedule_links(page):
    page.goto(BASE_URL, wait_until="networkidle")
    links = page.query_selector_all('#SchedulesPageLayout a')

    schedule_links = []
    for link in links:
        href = link.get_attribute("href")
        text = link.inner_text().strip()

        if href and "/schedule/" in href.lower():
            # FIX: convert relative → absolute
            if href.startswith("/"):
                href = "https://www.haysa.org" + href

            schedule_links.append({"url": href, "division": text})

    return schedule_links


def extract_schedule_table(page):
    # Wait for ANY Telerik schedule grid
    page.wait_for_selector("table[id*='ScheduleGrid']", timeout=60000)

    # Grab the first matching table
    html = page.inner_html("table[id*='ScheduleGrid']")

    df = pd.read_html(StringIO(html))[0]
    df.columns = ["Date", "Time", "Home", "Away", "Location"]
    return df


def clean_schedule_df(df, division):
    valid_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    df = df[df["Date"].astype(str).str[:3].isin(valid_days)]

    import re
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

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        links = get_schedule_links(page)

        all_frames = []
        for link in links:
            page.goto(link["url"], wait_until="domcontentloaded")

            print("Loaded:", link["url"])
            print("Page title:", page.title())
            print("HTML length:", len(page.content()))

            # Force JS hydration
            page.wait_for_timeout(2000)
            
            # Scroll to bottom to trigger lazy loading
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)

            df = extract_schedule_table(page)
            df = clean_schedule_df(df, link["division"])
            all_frames.append(df)

        browser.close()

    if not all_frames:
        print("No TS data found.")
        return

    ts_df = pd.concat(all_frames, ignore_index=True)
    write_df(ts_df, TS_SCHEDULE_RANGE)

if __name__ == "__main__":
    main()
