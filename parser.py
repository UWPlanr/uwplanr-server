import json
from db import get_client
from constants import COLLECTIONS, FACULTY_TO_COLLECTION

class Stack:
    def __init__(self):
        self.__stack = []
    def empty(self) -> bool:
        return not self.__stack
    def size(self) -> int:
        return len(self.__stack)
    def push(self, item):
        self.__stack.append(item)
    def pop(self):
        if self.empty():
            return None
        return self.__stack.pop()
    def output(self):
        print(self.__stack)

# Returns the lowest level operator with all the positions the operator occured.
# return: {
#   operator: str,
#   positions: list[int]
# }
# AAA 111 & BBB 222 & <CCC 333 | DDD 444> -> { operator: &, positions: [8, 18] }
def lowest_level_operator(string: str):
    brackets = Stack()
    llo = { "operator": "", "positions": [] }
    for i, character in enumerate(string):
        if character == "<":
            brackets.push("<")
        elif character == ">":
            brackets.pop()
        elif character == "|" or character == "&":
            if not brackets.empty():
                continue
            llo["operator"] = llo["operator"] or character
            llo["positions"].append(i)
        else:
            continue
    return llo

# Splits a string based on the indices while skipping the operators.
# AAA 111 & BBB 222 & <CCC 333 | DDD 444> -> [AAA 111, BBB 222, <CCC 333 | DDD 444>]
def split_string_by_indices(string: str, indices: list[int]):
    result = []
    start = 0
    for index in indices:
        result.append(string[start:index].strip())
        start = index + 1
    result.append(string[start:].strip())
    return result

# Generates a tree-based object version of the split requirements using the lowest level operator.
# AAA 111 & BBB 222 -> { operator: &, operands: [AAA 111, BBB 222] }
def tree_generator(expressions: list[str], llo: str):
    tree = { "operator": llo, "operands": [] }
    for expression in expressions:
        if expression.startswith("<") and expression.endswith(">"):
            expression = expression[1:len(expression) - 1]
            expression_llo = lowest_level_operator(expression)
            split_expression = split_string_by_indices(expression, expression_llo["positions"])
            tree["operands"].append(tree_generator(split_expression, expression_llo["operator"]))
        else:
            tree["operands"].append(expression)
    return tree

# General wrapper function for using the course requirement.
def tree_generator_wrapper(req: str):
    if req.strip() == "":
        return {}
    llo = lowest_level_operator(req)
    split_reqs = split_string_by_indices(req, llo["positions"])
    return tree_generator(split_reqs, llo["operator"])

# Checking if a courses requirements have been already parsed
def requirements_parsed(prereqs, coreqs) -> bool:
    return prereqs.startswith("{") and prereqs.endswith("}") and coreqs.startswith("{") and coreqs.endswith("}")

def main():
    db = get_client()

    courses = []
    for collection in COLLECTIONS:
        faculty_courses = list(db[collection].find({ "finalized": True }, projection={"_id": False}))
        courses = courses + faculty_courses

    for course in courses:
        if requirements_parsed(course["prereqs"], course["coreqs"]):
            print(f"Skipped {course['code']}.")
            continue
        parsed_prereqs = json.dumps(tree_generator_wrapper(course["prereqs"]))
        parsed_coreqs = json.dumps(tree_generator_wrapper(course["coreqs"]))
        db[FACULTY_TO_COLLECTION[course["faculty"]]].find_one_and_update({ "code": course["code"] }, { "$set": { "prereqs": parsed_prereqs, "coreqs": parsed_coreqs } })
        print(f"Updated {course['code']}.")

main()