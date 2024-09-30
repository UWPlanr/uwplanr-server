import re
from db import get_client
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright, expect

def run(playwright: Playwright) -> None:
    db = get_client()
    courses = list(db["courses"].find({ "finalized": True }, projection={ "_id": False }))

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    for course in courses:
        page.goto(f"https://uwflow.com/course/{course['code'].replace(' ', '').lower()}")
        page.get_by_text("%liked").click()
        elements = page.locator("div").filter(has_text=re.compile(r"^[0-9]{1,}%$")).all()

        statistics = [re.findall(r"[0-9]{1,}", element.text_content())[0] for element in elements]
        if len(statistics) != 5:
            print(f"UWFlow statistics not found/incomplete for {course['code']}.")
            continue
        statistics.pop(1) # Duplicate value for easy percentage
        statistics.pop(3) # Duplicate value for liked percentage
        statistics_object = { "liked": statistics[0], "easy": statistics[1], "useful": statistics[2], "lastUpdated": datetime.now().strftime("%d/%m/%Y") }
        
        db["courses"].find_one_and_update({ "finalized": True, "code": course["code"] }, { "$set": { "statistics": statistics_object } }, projection={ "_id": False })
        print(f"Updated {course['code']} with UWFlow statistics.")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)