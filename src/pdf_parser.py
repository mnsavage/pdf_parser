import json


class Pdf_Parser:
    def __init__(self, file_name):
        self._file_name = file_name

    def get_file_name(self):
        return self._file_name
