import pytest
from src.pdf_parser import Pdf_Parser


def test_init():
    file_name = "file/path/file.pdf"

    parser = Pdf_Parser(file_name)

    assert file_name == parser._file_name
