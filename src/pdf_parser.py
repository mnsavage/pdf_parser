import pdfminer
import pdfminer.high_level as pdf_hl
import pdfminer.layout as pdf_layout
import os
from page_parser import Page_Parser


class Pdf_Parser:
    def __init__(self, file_name):
        self._file_name = file_name
        self._pages = []
        self._page_handlers = []
        self._unpacked = False
        self._page_count = 0
        self._text_info = {}

    def get_pages(self):
        self.unpack()
        return self._pages
    
    def get_page_handlers(self):
        self.unpack()
        return self._page_handlers
    
    def get_page_count(self):
        self.unpack()
        return self._page_count
    
    def get_unpacked(self):
        return self._unpacked

    def unpack(self):
        if not self._unpacked:
            self._pages = pdf_hl.extract_pages(self._file_name)
            self._pages = list(self._pages)

            page_handlers = []
            for page in self._pages:
                self._page_handlers.append(Page_Parser(page))
            for ind, page in enumerate(self._page_handlers):
                page: Page_Parser
                page.unpack_page()

            self._page_count = len(self._page_handlers)
            self._unpacked = True

    def margin_check(self, leftWidth, rightWidth):
        self.unpack()
        for page in self._page_handlers:
            page: Page_Parser
            if page.content_bbox[0] < leftWidth:
                return False
            if page.content_bbox[2] > page.width - rightWidth:
                return False
        return True
    
    def margin_check_inches(self, leftWidth, rightWidth):
        self.unpack()
        leftWidth = self._inches_to_points(leftWidth)
        rightWidth = self._inches_to_points(rightWidth)
        return self.margin_check(leftWidth, rightWidth)
    
    def _inches_to_points(self, inches):
        return inches * 72
    

    #Super basic case
    #Return true if no pages are empty
    def check_empty_pages(self):
        self.unpack()
        for page in self._page_handlers:
            page: Page_Parser
            #If the content_bbox is unchanged from the default, return False
            if page.content_bbox == (None):
                return False
        return True
    
    #More advanced case, using the amount of filled space
    #Return true if no pages are empty
    def check_empty_pages_area(self, ratio=0.01):
        self.unpack()
        for page in self._page_handlers:
            page: Page_Parser
            #If the filled ratio is less than ratio, return False
            if not page.filled_ratio(ratio):
                return False
        return True
    
    #More advanced case, using the amount of filled space and the char count
    #Return true if no pages are empty
    def check_empty_pages_area_charcount(self, ratio=0.01, minchars=3):
        self.unpack()
        for page in self._page_handlers:
            page: Page_Parser
            # If the filled ratio is less than ratio, AND the char count is less than minchars, return False
            if not page.filled_ratio(ratio) and page.get_char_count() < minchars:
                return False
        return True
    
    def check_font_size_same_throughout_pdf(self):
        self.unpack()

        for page in self._page_handlers:
            page: Page_Parser
            font_sizes = page.all_sizes
            if len(set(font_sizes)) > 1:
                return False
            elif not font_sizes[12]:
                return False
        return True