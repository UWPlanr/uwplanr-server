import re

# At least 1 unit in ABC at the Z00-level or above -> ABC ZXX+
# Any Z00-level AAA or BBB course -> AAA ZXX or BBB ZXX
# At least 1 unit in a Z00-level ABC course -> ABC ZXX
# Z00-level ABC course -> ABC ZXX
# At least 1 unit in AAA or BBB -> AAA XXX or BBB XXX
def only_codes(string):
    string = re.sub(r"[Aa]t least 1 unit in ([A-Z]{2,})(?: course)? at the ([0-9])00-level or above", r"\1 \2XX+", string)
    string = re.sub(r"[Aa]ny ([0-9])00-level ([A-Z]{2,}) or ([A-Z]{2,}) course", r"\2 \1XX or \3 \1XX", string)
    string = re.sub(r"[Aa]t least 1 unit in a ([0-9])00-level ([A-Z]{2,}) course", r"\2 \1XX", string)
    string = re.sub(r"([0-9])00-level ([A-Z]{2,}) course", r"\2 \1XX", string)
    string = re.sub(r"[Aa]t least 1 unit in ([A-Z]{2,}) or ([A-Z]{2,})", r"\1 XXX or \2 XXX", string)
    return string

# ABC/DEF 123 -> ABC 123/DEF 123 | ABC or DEF 123 -> ABC 123 or DEF 123
def two_subjects_one_code(string):
    return re.sub(r"([A-Z]{2,})\s?(/|or)\s?([A-Z]{2,})\s?([0-9]{3}[A-Z]?)", r"\1 \4 \2 \3 \4", string)

# ABC 123/456 -> ABC 123/ABC 456 | ABC 123 or 456 -> ABC 123 or ABC 456
def one_subject_two_codes(string):
    return re.sub(r"([A-Z]{2,})\s?([0-9]{3}[A-Z]?)\s?(/|or)\s?([0-9]{3}[A-Z]?)", r"\1 \2 \3 \1 \4", string)

# ABC 111, 222, 333, ... -> ABC 111, ABC 222, ABC 333, ...
def one_subject_multiple_codes(string):
    many_catalog_numbers = re.findall(r"[A-Z]{2,}\s?(?:[0-9]{3}[A-Z]?,\s?)+[0-9]{3}[A-Z]?", string)
    for match in many_catalog_numbers:
        subject_code = re.findall(r"[A-Z]{2,}", match)[0]
        catalog_numbers = re.findall(r"[0-9]{3}[A-Z]?", match)
        expanded_string = ", ".join([f"{subject_code} {catalog_number}" for catalog_number in catalog_numbers])
        string = string.replace(match, expanded_string)
    return string

# One of AAA 111, BBB 222, CCC 333, ... -> (AAA 111 or BBB 222 or CCC 333 or ...)
def one_ofs(string):
    one_ofs = re.findall(r"\(?[Oo]ne of (?:[A-Z]{2,}\s?[0-9]{3}[A-Z]?(?:\s{[0-9]{2,}%})?(?:,\s)?)+\)?", string)
    for match in one_ofs:
        codes = re.findall(r"[A-Z]{2,}\s?[0-9]{3}[A-Z]?(?:\s{[0-9]{2,}%})?", match)
        or_string = " or ".join(codes)
        string = string.replace(match, f"({or_string})")
    return string

# [Variations below] -> ABC 123 {XY%}
# ABC 123 with at least XY% | ABC 123 with a grade of XY% | ABC 123 with a grade of at least XY%
# At least XY% in ABC 123 | ABC 123 with minimum grade of XY% | ABC 123 with a minimum grade of XY%
# a grade of XY% or higher in XY%
# ADD: ABC 123 (minimum grade of XY%)
def course_grades(string):
    string = re.sub(r"([A-Z]{2,}\s?[0-9]{3}[A-Z]?) with (?:(?:at least|a grade of(?: at least)?)) ([0-9]{2,}%)", r"\1 {\2}", string)
    string = re.sub(r"[Aa]t least ([0-9]{2,}%) in ([A-Z]{2,}\s?[0-9]{3}[A-Z]?)", r"\2 {\1}", string)
    string = re.sub(r"([A-Z]{2,}\s?[0-9]{3}[A-Z]?) with (?:a\s)?minimum grade of ([0-9]{2,}%)", r"\1 {\2}", string)
    string = re.sub(r"a grade of ([0-9]{2,}%) or higher in ([A-Z]{2,}\s?[0-9]{3}[A-Z]?)", r"\2 {\1}", string)
    return string

# X 1111, 2222, 3333 -> X 1111, X 2222, X 3333
def one_term_multiple_years(string):
    multiple_years = re.findall(r"(?:[Ss]pring|[Ww]inter|[Ff]all) (?:[0-9]{4},?\s?)+", string)
    for match in multiple_years:
        if match[-2:] == ", ":
            match = match[:-2]
        term = re.findall(r"(?:[Ss]pring|[Ww]inter|[Ff]all)", match)[0]
        years = re.findall(r"[0-9]{4}", match)
        final_string = ", ".join([f"{term} {year}" for year in years])
        string = string.replace(match, final_string)
    return string

# spring 2021, winter 2022 -> S21, W22
def condense_terms(string):
    expanded_dates = re.findall(r"(?:[Ss]pring|[Ff]all|[Ww]inter)\s[0-9]{4}", string)
    for match in expanded_dates:
        condensed_term = f"{match[0].upper()}{match[-2:]}"
        string = string.replace(match, condensed_term)
    return string

# ABC 123 taken X11, Y22, Z33, ... -> ABC 123 taken X11, ABC 123 taken Y22, ABC 123 taken Z22, ..
def one_course_multiple_terms(string):
    course_multiple_terms = re.findall(r"[A-Z]{2,}\s?[0-9]{3}[A-Z]? taken (?:in\s)?(?:(?:S|F|W)[0-9]{2}(?:,\s)?)+", string)
    for match in course_multiple_terms:
        code = re.findall(r"[A-Z]{2,}\s?[0-9]{3}[A-Z]?", match)[0]
        terms = re.findall(r"(?:S|F|W)[0-9]{2}", match)
        final_string = ", ".join([f"{code} taken {term}" for term in terms])
        string = string.replace(match, final_string)
    return string

# [Variations below] -> ABC 123 [X12] | ABC 123 [X12+] | ABC 123 [X12-]
# ABC 123 taken X12 | ABC 123 456 X12 | ABC 123 456 taken in X12
# ABC 123 X12 456 | ABC 123 (Topic: ...) taken X12 | ABC 123 (456) X12
# ABC 123 (LEC 456) taken X12 | ABC 123 after X12 | ABC 123 taken prior to X12
# ABC 123 taken before X12
def course_terms(string):
    string = re.sub(r"([A-Z]{2,}\s?[0-9]{3}[A-Z]?) taken ((?:F|W|S)[0-9]{2})", r"\1 [\2]", string)
    string = re.sub(r"([A-Z]{2,}\s?[0-9]{3}[A-Z]?) [0-9]{3} (?:taken in\s)?((?:F|W|S)[0-9]{2})", r"\1 [\2]", string)
    string = re.sub(r"([A-Z]{2,}\s?[0-9]{3}[A-Z]?) ((?:F|W|S)[0-9]{2}) [0-9]{3}", r"\1 [\2]", string)
    string = re.sub(r"([A-Z]{2,}\s?[0-9]{3}[A-Z]?) \(Topic:.*\) taken ((?:F|W|S)[0-9]{2})", r"\1 [\2]", string)
    string = re.sub(r"([A-Z]{2,}\s?[0-9]{3}[A-Z]?) \([0-9]{3}\) ((?:F|W|S)[0-9]{2})", r"\1 [\2]", string)
    string = re.sub(r"([A-Z]{2,}\s?[0-9]{3}[A-Z]?) \([A-Z]{3}\s[0-9]{3}\) taken ((?:F|W|S)[0-9]{2})", r"\1 [\2]", string)
    string = re.sub(r"([A-Z]{2,}\s?[0-9]{3}[A-Z]?) after ((?:F|W|S)[0-9]{2})", r"\1 [\2+]", string)
    string = re.sub(r"([A-Z]{2,}\s?[0-9]{3}[A-Z]?) taken (?:prior to|before) ((?:F|W|S)[0-9]{2})", r"\1 [\2-]", string)
    return string

# [Requirements string] -> [Lowest term required to take a course]
def lowest_term(string):
    if not string:
        return ""
    terms = re.findall(r"(?:\s)([0-9][AB])", string)
    if len(terms) == 0:
        return ""
    else:
        return min(terms, key=lambda term: (int(term[0]), term[1]))

# Offered: X, Y, Z -> [X, Y, Z]
def terms_offered(string):
    terms_offered_match = re.findall(r"[Oo]ffered:\s?(?:[A-Z],?\s?)+", string)
    if not terms_offered_match:
        return []
    return re.findall(r"(F|W|S)", terms_offered_match[0])

# AAA 111(separator)BBB 222 ... -> AAA 111(replacement)BBB 222 ...
def replace_code_separator_with(separator, replacement, string):
    regex = "(?:[A-Z]{2,}\s?[0-9]{3}[A-Z]?(?:\s{[0-9]{2,}%})?(?:" + separator + ")?)+"
    matches = re.findall(regex, string)
    for match in matches:
        replacement_string = replacement.join(match.split(separator))
        string = string.replace(match, replacement_string)
    return string

# Returns parsed prerequisites (NEEDS WORK)
def parse_prereqs(prereqs):
    # Parsing prerequisites to an intermediate string
    prereqs = only_codes(prereqs)
    prereqs = two_subjects_one_code(prereqs)
    prereqs = one_subject_two_codes(prereqs)
    prereqs = one_subject_multiple_codes(prereqs)
    prereqs = course_grades(prereqs)
    prereqs = one_ofs(prereqs)

    # Remove any terms and non-course grade requirements
    prereqs = re.sub(r"\s[0-9][AB]\s?", "", prereqs)
    prereqs = re.sub(r"\s[0-9]{2,}%", "", prereqs)

    # (AAA 111 or BBB 222) -> <AAA 111 or BBB 222>
    prereqs = prereqs.replace("(", "<").replace(")", ">")

    # Replace [" and ", "; ", ", "] separators between codes with " & "
    prereqs = replace_code_separator_with(" and ", " & ", prereqs)
    prereqs = replace_code_separator_with("; ", " & ", prereqs)
    prereqs = replace_code_separator_with(", ", " & ", prereqs)

    # Replace [" or ", "/"] separators between codes with " | "
    prereqs = replace_code_separator_with(" or ", " | ", prereqs)
    prereqs = replace_code_separator_with("/", " | ", prereqs)

    # Remove all words and unnecessary characters
    prereqs = re.sub(r"[a-zA-Z\\-]*[a-z][a-zA-Z\\-]*", "", prereqs)
    prereqs = prereqs.replace(";", "").replace("/", "").replace(",", "")

    # Remove extra spaces
    prereqs = re.sub(r"\s\s+", " ", prereqs)

     # Remove empty "< >" substrings
    prereqs = prereqs.replace("< >", "")

    return prereqs

# Returns parsed prerequisites
def parse_antireqs(antireqs):
    # Parsing terms antirequisites to condensed form
    antireqs = one_term_multiple_years(antireqs)
    antireqs = condense_terms(antireqs)
    antireqs = one_course_multiple_terms(antireqs)
    antireqs = course_terms(antireqs)

    # Parsing antirequisites to an intermediate string
    antireqs = one_subject_two_codes(antireqs)
    antireqs = two_subjects_one_code(antireqs)
    antireqs = one_subject_multiple_codes(antireqs)

    antireqs = ",".join(re.findall(r"[A-Z]{2,}\s?[0-9]{3}[A-Z]?(?:\s\[(?:S|F|W)[0-9]{2}\])?", antireqs))

    return antireqs

# Returns parsed corequisites
def parse_coreqs(coreqs):
    # Parsing corequisites to an intermediate string
    coreqs = two_subjects_one_code(coreqs)
    coreqs = one_subject_two_codes(coreqs)
    coreqs = one_subject_multiple_codes(coreqs)
    coreqs = one_ofs(coreqs)

    # Replace "(" with "<" and ")" with ">"
    coreqs = coreqs.replace("(", "<").replace(")", ">")

    # Replace [" and ", "; ", ", "] separators between codes with " & "
    coreqs = replace_code_separator_with(" and ", " & ", coreqs)
    coreqs = replace_code_separator_with("; ", " & ", coreqs)
    coreqs = replace_code_separator_with(", ", " & ", coreqs)

    # Replace [" or ", "/"] separators between codes with " | "
    coreqs = replace_code_separator_with(" or ", " | ", coreqs)
    coreqs = replace_code_separator_with("/", " | ", coreqs)

    # Remove all words and unnecessary characters
    coreqs = re.sub(r"[a-zA-Z\\-]*[a-z][a-zA-Z\\-]*", "", coreqs)
    coreqs = coreqs.replace(";", "").replace("/", "").replace(",", "")

    # Remove extra spaces
    coreqs = re.sub(r"\s\s+", " ", coreqs)

    # Remove empty "< >" substrings
    coreqs = coreqs.replace("< >", "")

    return coreqs