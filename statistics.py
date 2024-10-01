import re
from db import get_client
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    db = get_client()
    courses = list(db["courses"].find({ "finalized": True }, projection={ "_id": False }))

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    current_date = datetime.now().strftime("%d/%m/%Y")

    for course in courses:
        if "statistics" in course and "lastUpdated" in course["statistics"] and course["statistics"]["lastUpdated"] == current_date:
            print(f"{course['code']} already has been updated with UWFlow statistics as of {course['statistics']['lastUpdated']}")
            continue

        page.goto(f"https://uwflow.com/course/{course['code'].replace(' ', '').lower()}")
        page.get_by_text("liked").first.click()
        elements = page.locator("div").filter(has_text=re.compile(r"^(?:([0-9]{1,}%)|(N/A))$")).all()

        stats = [re.findall(r"(?:(?:[0-9]{1,})|(?:N/A))", element.text_content())[0] for element in elements]
        if len(stats) != 5:
            print(f"UWFlow statistics not found/incomplete for {course['code']}.")
            continue
        stats.pop(1) # Duplicate value for easy percentage
        stats.pop(3) # Duplicate value for liked percentage
        current_date = datetime.now().strftime("%d/%m/%Y")
        stats_object = { "liked": stats[0], "easy": stats[1], "useful": stats[2], "lastUpdated": current_date }
        

        db["courses"].find_one_and_update({ "finalized": True, "code": course["code"] }, { "$set": { "statistics": stats_object } }, projection={ "_id": False })
        print(f"Updated {course['code']} with UWFlow statistics.")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)