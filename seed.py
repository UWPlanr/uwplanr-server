import os
import re
import sys
import requests
from db import get_client
from dotenv import load_dotenv
from constants import FACULTIES, FACULTY_TO_COLLECTION
from helpers import parse_prereqs, parse_coreqs, parse_antireqs, lowest_term, terms_offered

load_dotenv()

# Checks if a course falls under one of the six faculties and it is an undergraduate course.
def valid_course(course) -> bool:
    if course["associatedAcademicGroupCode"] in FACULTIES and course["associatedAcademicCareer"] == "UG":
        return True
    return False

# Splits the requirement string into a dictionary with prereqs, coreqs and antireqs
def requirement_splitter(requirement: str) -> dict[str, str]:
    result = { "prereqs": "", "coreqs": "", "antireqs": "" }

    if not requirement:
        return result

    requirement = requirement.replace("0.50", "1").replace("1.00", "2").replace("1.50", "3").replace("2.00", "4").replace("2.50", "5")
    requirement = requirement.replace("0.5", "1").replace("1.0", "2").replace("1.5", "3").replace("2.0", "4").replace("2.5", "5")
    requirement = requirement.replace("&", "and").replace("|", "or")

    prereqs_match = re.search(r"Prereq: ([^.]*)", requirement)
    coreqs_match = re.search(r"Coreq: ([^.]*)", requirement)
    antireqs_match = re.search(r"Antireq: ([^.]*)", requirement)

    if prereqs_match:
        result["prereqs"] = prereqs_match.group(1).strip()
    if coreqs_match:
        result["coreqs"] = coreqs_match.group(1).strip()
    if antireqs_match:
        result["antireqs"] = antireqs_match.group(1).strip()
    return result

def main():
    if not (len(sys.argv) == 2 and sys.argv[1].isnumeric()):
        print("Please specify an appropriate term courses required.")
        return
    
    # Requesting courses from UW API
    url = f"https://openapi.data.uwaterloo.ca/v3/Courses/{sys.argv[1]}/"
    response = requests.get(url, headers={ "x-api-key": os.getenv("UW_API_KEY") })

    if response.status_code != 200:
        print("Term courses not found")
    courses = response.json()

    db = get_client()

    for course in courses:
        if valid_course(course):
            subject_code, catalog_number, faculty = course["subjectCode"], course["catalogNumber"], course["associatedAcademicGroupCode"]
            title, description, requirements = course["title"], course["description"], course["requirementsDescription"]
            code = f"{subject_code} {catalog_number}"

            # Checking if the course exists in the database and has the same requirements and description
            course_in_db = db[FACULTY_TO_COLLECTION[faculty]].find_one({ "code": code })
            if course_in_db is not None:
                if course_in_db["requirements"] == requirements and course_in_db["description"] == description:
                    continue
                else:
                    db[FACULTY_TO_COLLECTION[faculty]].delete_one({ "code": code })
            
            split_reqs = requirement_splitter(requirements)
            prereqs = parse_prereqs(split_reqs["prereqs"])
            coreqs = parse_coreqs(split_reqs["coreqs"])
            antireqs = parse_antireqs(split_reqs["antireqs"])
            min_level = lowest_term(requirements)
            offerings = terms_offered(description)

            data = {
                "code": code,
                "title": title,
                "faculty": faculty,
                "description": description,
                "requirements": requirements,
                "prereqs": prereqs,
                "coreqs": coreqs,
                "antireqs": antireqs,
                "termsOffered": offerings,
                "minLevel": min_level,
                "finalized": False,
            }

            db[FACULTY_TO_COLLECTION[faculty]].insert_one(data)
            print(f"Added {code} to MongoDB.")

main()