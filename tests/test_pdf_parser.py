import pytest
from src.pdf_parser import Pdf_Parser
from src.page_parser import Page_Parser
import os

def test_init():
    file_name = "file/path/file.pdf"

    parser = Pdf_Parser(file_name)

    assert file_name == parser._file_name

def test_unpack():
    #Select a PDF file to test with, assert that there are pages
    #Assert that our parser has the pages and page handlers stored
    file_name = "Homework_1.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    parser.unpack()

    assert len(parser._pages) > 0
    assert len(parser._page_handlers) > 0
    assert parser.get_unpacked() == True

def test_margin_check():
    #Select a PDF file to test with, assert that the margins are good
    file_name = "Homework_1.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.margin_check(72, 72) == True

def test_margin_check_bad():
    #Select a PDF file to test with, assert that the margins are good
    file_name = "bad_margins.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.margin_check(72, 72) == False

def test_pages_empty():
    #Select a PDF file to test with, assert that there are no empty pages
    file_name = "Homework_1.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_empty_pages_area_charcount() == True

#TODO: Write tests for bold, font size, and font name

def test_no_bold_in_preliminary_pages():
    #Select a PDF file to test with, assert that there are no bold characters in the preliminary pages
    file_name = "example_thesis_caroline.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_bold_in_preliminary_pages() == True

def test_font_size():
    #Select a PDF file to test with, assert that there are no font size changes in the preliminary pages
    file_name = "example_thesis_caroline.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_font_size_same_throughout_pdf() == True

def test_font_name():
    #Select a PDF file to test with, assert that there are no font name changes in the preliminary pages
    file_name = "example_thesis_caroline.pdf"
    file_name_path = os.path.join(
        os.path.dirname(__file__), "..", "prototyping", file_name
    )
    parser = Pdf_Parser(file_name_path)

    assert parser.check_font_same_throughout_pdf() == True