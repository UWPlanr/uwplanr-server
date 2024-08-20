from helpers import *

def tests():
    assert(two_subjects_one_code("GRK/RS 101") == "(GRK 101 / RS 101)")
    assert(two_subjects_one_code("GRK / RS 101") == "(GRK 101 / RS 101)")
    assert(two_subjects_one_code("SOC/LS 150R") == "(SOC 150R / LS 150R)")
    assert(two_subjects_one_code("SOC or LS 150R") == "(SOC 150R or LS 150R)")

    assert(one_subject_two_codes("MATH 118/119") == "(MATH 118 / MATH 119)")
    assert(one_subject_two_codes("MATH 237 or 247") == "(MATH 237 or MATH 247)")

    assert(one_subject_multiple_codes("MATH 114, 115, 116, 117, 135, 145") == "MATH 114, MATH 115, MATH 116, MATH 117, MATH 135, MATH 145")
    assert(one_subject_multiple_codes("PHYS 111, 112, MATH 135, 136") == "PHYS 111, PHYS 112, MATH 135, MATH 136")

    assert(one_ofs("One of MATH 138, MATH 148") == "(MATH 138 or MATH 148)")
    assert(one_ofs("One of MATH 138 {60%}, MATH 148") == "(MATH 138 {60%} or MATH 148)")
    assert(one_ofs("one of MATH 138, MATH 148") == "(MATH 138 or MATH 148)")
    assert(one_ofs("One of MATH 138 {60%}, MATH 148; One of MATH 136 {60%}, MATH 146") == "(MATH 138 {60%} or MATH 148); (MATH 136 {60%} or MATH 146)")

    assert(one_term_multiple_years("winter 2015, 2016") == "winter 2015, winter 2016")
    assert(one_term_multiple_years("winter 2015, 2016, spring 2017, 2018, 2019") == "winter 2015, winter 2016, spring 2017, spring 2018, spring 2019")

    assert(condense_terms("REES 260 taken in spring 2024, fall 2022") == "REES 260 taken in S24, F22")
    assert(condense_terms("REES 260 taken in Spring 2024") == "REES 260 taken in S24")
    assert(condense_terms("REES 260 taken in winter 2022, winter 2021, fall 2019") == "REES 260 taken in W22, W21, F19")

    assert(one_course_multiple_terms("REES 260 taken S24, F22") == "REES 260 taken S24, REES 260 taken F22")
    assert(one_course_multiple_terms("REES 260 taken in S24, F22") == "REES 260 taken S24, REES 260 taken F22")

    assert(course_terms("REES 260 taken S24, REES 260 taken F22") == "REES 260 [S24], REES 260 [F22]")
    assert(course_terms("GRK 101 001 S20") == "GRK 101 [S20]")
    assert(course_terms("GRK 101 001 taken in S20") == "GRK 101 [S20]")
    assert(course_terms("GRK 101 S20 001") == "GRK 101 [S20]")

    assert(lowest_term("Level at least 2A") == "2A")
    assert(lowest_term("(ECE 140, 240; Level at least 2B Computer Engineering or Electrical Engineering) or (ECE 140, MATH 213; Level at least 3A Software Engineering)") == "2B")
    assert(lowest_term(" Level at least 3A Knowledge Integration or Level at least 4A") == "3A")

    assert(terms_offered("Offered: F,W,S") == ["F", "W", "S"])
    assert(terms_offered("Offered: F, W,S") == ["F", "W", "S"])
    assert(terms_offered("Offered: F, W") == ["F", "W"])
    assert(terms_offered("Offered: S") == ["S"])

    assert(course_grades("MATH 138 with at least 60%") == "MATH 138 {60%}")
    assert(course_grades("MATH 138 with a grade of 60%") == "MATH 138 {60%}")
    assert(course_grades("MATH 138 with a grade of at least 60%") == "MATH 138 {60%}")
    assert(course_grades("MATH 138 with a minimum grade of 60%") == "MATH 138 {60%}")
    assert(course_grades("MATH 138 with minimum grade of 60%") == "MATH 138 {60%}")
    assert(course_grades("At least 60% in MATH 138") == "MATH 138 {60%}")
    assert(course_grades("a grade of 60% or higher in MATH 138") == "MATH 138 {60%}")

tests()