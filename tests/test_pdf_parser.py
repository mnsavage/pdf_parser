from src.pdf_parser import Pdf_Parser
import os


def test_init():
    file_name = "file/path/file.pdf"

    parser = Pdf_Parser(file_name)

    assert file_name == parser._file_name


def test_font_name():
    # Select a PDF file to test with, assert that there are no font name changes in the preliminary pages
    file_name = "example_thesis_caroline.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_font_not_same_throughout_pdf() is True


def test_unpack():
    # Select a PDF file to test with, assert that there are pages
    # Assert that our parser has the pages and page handlers stored
    file_name = "Homework_1.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    parser.unpack()

    assert len(parser._pages) > 0
    assert len(parser._page_handlers) > 0
    assert parser.get_unpacked() is True


def test_margin_check():
    # Select a PDF file to test with, assert that the margins are good
    file_name = "Homework_1.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.margin_check(72, 72) is False


def test_margin_check_bad():
    # Select a PDF file to test with, assert that the margins are good
    file_name = "bad_margins.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.margin_check(72, 72) is True


def test_no_pages_empty():
    # Select a PDF file to test with, assert that there are no empty pages
    file_name = "Homework_1.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_no_empty_pages_area_charcount() is False


# TODO: Write tests for bold, font size, and font name


def test_no_bold_in_preliminary_pages():
    # Select a PDF file to test with, assert that there are no bold characters in the preliminary pages
    file_name = "example_thesis_caroline.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_bold_in_preliminary_pages() is False


def test_font_size_not_same_throughout_pdf():
    # Select a PDF file to test with, assert that there are no font size changes in the preliminary pages
    file_name = "example_thesis_caroline.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_font_size_not_same_throughout_pdf() is True


def test_font_not_same_throughout_pdf():
    # Select a PDF file to test with, assert that there are no font name changes in the preliminary pages
    file_name = "example_thesis_caroline.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_font_not_same_throughout_pdf() is True


def test_get_file_name():
    file_name = "file/path/file.pdf"

    parser = Pdf_Parser(file_name)

    assert file_name == parser.get_file_name()


# MARK: testing function: check_by_not_lowercase
def test_by_in_title_pass():
    # Test that a "by" that is correctly formatted will pass
    file_name = "correct_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_by_not_lowercase() is False


def test_by_in_title_fail_formatting():
    # Test that a "by" that is capitalized will fail
    file_name = "by_incorrect_format.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_by_not_lowercase() is True


def test_by_in_title_fail_existance():
    # Test that a "by" that is not in the title page will fail
    file_name = "no_by_in_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_by_not_lowercase() is True


# MARK: testing function: check_chair_requirement_incorrect
def test_chair_requirement_pass():
    # Test that having one chair and one co chair will pass
    file_name = "correct_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_chair_requirement_incorrect() is False


def test_chair_requirement_pass_no_co_chair():
    # Test that having one chair an no co chair will pass
    file_name = "no_co_chair.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_chair_requirement_incorrect() is False


def test_chair_requirement_fail_no_chair():
    # Test that having no chair will fail
    file_name = "no_chair.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_chair_requirement_incorrect() is True


def test_chair_requirement_fail_two_co_chairs():
    # Test that having more than one co chair will fail
    file_name = "two_co_chairs.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_chair_requirement_incorrect() is True


# MARK: testing function: check_department_incorrect
def test_department_pass():
    # Test that having the department passes
    file_name = "correct_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_department_incorrect() is False


def test_department_fail():
    # Test that not having the department fails
    file_name = "missing_department.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_department_incorrect() is True


# MARK: testing function: check_location_requirement_incorrect
def test_location_requirement_pass():
    # Test that correctly formatting the location passes
    file_name = "correct_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_location_requirement_incorrect() is False


def test_location_requirement_fail_location_not_fully_written():
    # Test that writing "AL" instead of "ALABAMA" fails
    file_name = "location_not_fully_written.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_location_requirement_incorrect() is True


def test_location_requirement_fail_location_not_all_caps():
    # Test that not having location in all caps fails
    file_name = "location_not_all_caps.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_location_requirement_incorrect() is True


# MARK: testing function: check_graduation_year_incorrect
def test_graduation_year_pass():
    # Test that graduation year found at bottom passes
    file_name = "correct_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_graduation_year_incorrect() is False


def test_graduation_year_fail_year_not_bottom():
    # Test that writing graduation year not at the very bottom fails
    file_name = "year_not_bottom.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_graduation_year_incorrect() is True


def test_graduation_year_fail_year_with_word():
    # Test that having characters in the graduation year fails
    file_name = "year_with_word.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_graduation_year_incorrect() is True


# MARK: testing function: get_paper_type
def test_get_paper_type_pass_dissertation():
    # Test that paper is dissertation
    file_name = "correct_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.get_paper_type() == "dissertation"


def test_get_paper_type_pass_thesis():
    # Test that paper is a thesis
    file_name = "thesis.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.get_paper_type() == "thesis"


def test_get_paper_type_fail_none_found():
    # Test that paper not having thesis or dissertation fails
    file_name = "no_thesis_or_dissertation.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.get_paper_type() is False


# MARK: testing function: get_student_name
def test_get_student_name_pass():
    # Test that paper gets student fname and lname
    file_name = "student_name.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.get_student_name()["fname"] == "STUDENTFNAME"
    assert parser.get_student_name()["lname"] == "STUDENTLNAME"


def test_get_student_name_pass_mname_in_fname():
    # Test that paper gets student fname and lname if a mname is included
    file_name = "student_with_mname.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.get_student_name()["fname"] == "STUDENTFNAME STUDENTMNAME"
    assert parser.get_student_name()["lname"] == "STUDENTLNAME"


def test_get_student_name_fail_no_by_found():
    # Test that paper fails if if by is not found
    file_name = "no_by_in_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.get_student_name() is False


# MARK: testing function: check_title_format_incorrect
def test_title_format_pass():
    # Test that the title formatting is correct
    file_name = "correct_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_title_format_incorrect() is False


def test_title_format_fail_2_lines():
    # Test that a title with 2 lines fail
    file_name = "title_2_lines.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_title_format_incorrect() is True


def test_title_format_fail_4_lines():
    # Test that having a title with 4 lines fails
    file_name = "title_4_lines.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_title_format_incorrect() is True


def test_title_format_fail_1_5_spacing():
    # Test that having a title that is 1.5 spacing fails
    file_name = "title_1_5_spacing.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_title_format_incorrect() is True


def test_title_format_fail_2_5_spacing():
    # Test that having a title that is 2.5 spacing fails
    file_name = "title_2_5_spacing.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_title_format_incorrect() is True


def test_title_format_fail_mixed_spacing():
    # Test that having a title that has mixed spacing fails
    file_name = "title_mixed_spacing.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_title_format_incorrect() is True


def test_title_format_fail_middle_line_longest():
    # Test that having a title that has middle line longest
    file_name = "title_middle_line_longest.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_title_format_incorrect() is True


def test_title_format_fail_last_line_longest():
    # Test that having a title that the last line longest
    file_name = "title_last_line_longest.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_title_format_incorrect() is True


# MARK: testing function: check_spacing_beneath_title_incorrect
def test_spacing_beneath_title_pass():
    # Test that two double spaces beneath title pass
    file_name = "correct_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_spacing_beneath_title_incorrect() is False


def test_spacing_beneath_title_fail_one_space():
    # Test that only one line beneath title fails
    file_name = "one_space_beneath_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_spacing_beneath_title_incorrect() is True


def test_spacing_beneath_title_fail_1_5_spaced():
    # Test that lines under title that are 1.5 spaced fails
    file_name = "1_5_spaced_beneach_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_spacing_beneath_title_incorrect() is True


def test_spacing_beneath_title_fail_2_5_spaced():
    # Test that lines under title that are 2.5 spaced fails
    file_name = "2_5_spaced_beneach_title.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_spacing_beneath_title_incorrect() is True
