import pdfminer.high_level as pdf_hl
from pdfminer.layout import LTTextContainer
from page_parser import Page_Parser


class Pdf_Parser:
    def __init__(self, file_name):
        self._file_name = file_name
        self._pages = []
        self._first_page_contents = []
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

            # custom sorting to make sure the higher y val goes first in the list
            def sort_by_ypos(e):
                return e.y0

            firstPage = list(self._pages[0])
            firstPage.sort(key=sort_by_ypos, reverse=True)
            self._first_page_contents = firstPage

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
                return True
            if page.content_bbox[2] > page.width - rightWidth:
                return True
        return False

    def margin_check_inches(self, leftWidth, rightWidth):
        self.unpack()
        leftWidth = self._inches_to_points(leftWidth)
        rightWidth = self._inches_to_points(rightWidth)
        return self.margin_check(leftWidth, rightWidth)

    def _inches_to_points(self, inches):
        return inches * 72

    # Super basic case
    # Return true if no pages are empty
    def check_no_empty_pages(self):
        self.unpack()
        for page in self._page_handlers:
            page: Page_Parser
            # If the content_bbox is unchanged from the default, return False
            if page.content_bbox == (None):
                return True
        return False

    # More advanced case, using the amount of filled space
    # Return true if no pages are empty
    def check_empty_pages_area(self, ratio=0.01):
        self.unpack()
        for page in self._page_handlers:
            page: Page_Parser
            # If the filled ratio is less than ratio, return False
            if not page.filled_ratio(ratio):
                return False
        return True

    # More advanced case, using the amount of filled space and the char count
    # Return true if no pages are empty
    def check_no_empty_pages_area_charcount(self, ratio=0.01, minchars=3):
        self.unpack()
        for page in self._page_handlers:
            page: Page_Parser
            # If the filled ratio is less than ratio, AND the char count is less than minchars, return True
            if not page.filled_ratio(ratio) and page.get_char_count() < minchars:
                return True
        return False

    def check_font_size_not_same_throughout_pdf(self):
        self.unpack()

        for page in self._page_handlers:
            page: Page_Parser
            font_sizes = page.all_sizes
            if len(set(font_sizes)) > 1:
                return True
            elif not font_sizes[12]:
                return True
        return False

    def _normalize_font_name(self, font_name):
        # Remove subset tag, if exists
        if "+" in font_name:
            font_name = font_name.split("+")[-1]

        # Lowercase the font name for uniformity
        font_name = font_name.lower()

        # Define a list of style and weight indicators to remove
        style_indicators = [
            "bold",
            "italic",
            "oblique",
            "regular",
            "bd",
            "it",
            "lt",
            "med",
            "heavy",
            "black",
            "light",
            "-",
        ]

        # Remove these indicators
        for indicator in style_indicators:
            font_name = font_name.replace(indicator, "")

        # Handle special cases (like 'MT' in 'ArialMT')
        special_cases = {"mt": ""}
        for case in special_cases:
            font_name = font_name.replace(case, special_cases[case])

        return font_name.strip()

    def check_font_not_same_throughout_pdf(self):
        self.unpack()
        base_fonts = set()
        auxiliary_fonts = {"symbol", "arial"}  # Add more if needed

        for page in self._page_handlers:
            page: Page_Parser
            fonts = page.all_fontnames

            normalized_fonts = {self._normalize_font_name(font) for font in fonts}

            # Filter out auxiliary fonts if other fonts are present
            # This is because subscript/superscript characters are often in auxiliary fonts even though the main text is in a different font
            if len(normalized_fonts.difference(auxiliary_fonts)) > 0:
                normalized_fonts -= auxiliary_fonts

            base_fonts.update(normalized_fonts)

            if len(base_fonts) > 1:
                for font in base_fonts:
                    print(font)
                return True

        return False

    def check_bold_throughout_pdf(self):
        self.unpack()

        for page in self._page_handlers:
            page: Page_Parser
            fonts = page.all_fontnames
            for font in fonts:
                if page.is_bold(font):
                    return True
        return False

    def _find_preliminary_pages(self):
        self.unpack()

        preliminary_pages = []
        for page in self._page_handlers:
            page: Page_Parser
            if page.is_preliminary_page():
                preliminary_pages.append(page)

        return preliminary_pages

    def check_bold_in_preliminary_pages(self):
        self.unpack()

        preliminary_pages = self._find_preliminary_pages()

        for page in preliminary_pages:
            page: Page_Parser
            fonts = page.all_fontnames
            for font in fonts:
                if page.is_bold(font):
                    return True
        return False

    # MARK: Check title page for thesis/dissertation

    # check for the location of "by" in the title page
    # and if it is correctly formated to be lowercase
    # if there is no by, return -1
    def _check_by(self):
        self.unpack()

        for index, text in enumerate(self._first_page_contents):
            if text.get_text().strip().lower() == "by":
                return {
                    "found_location": index,
                    "correct_format": text.get_text().islower(),
                }
        return {"found_location": -1}  # should throw/ display error here

    # check the spacing between lines
    #   lines: an array of lines to check spacing between
    #   returns: the spacing type (1, 1.5, 2, 2.5, 3)
    #   returns -1 if lines is an array with less than 2 elements
    #   or if the line spacing is not consistant throughout
    def _check_line_spacing(self, lines):
        self.unpack()

        # custom sorting to make sure the higher y val goes first in the list
        def sort_by_ypos(e):
            return e.y0

        # make sure the lines are sorted
        lines.sort(key=sort_by_ypos, reverse=True)

        if len(lines) < 2:
            return -1
        spacing = 0
        for lineNum in range(len(lines) - 1):
            current = lines[lineNum]
            next = lines[lineNum + 1]
            curSize = current.y1 - current.y0
            between = current.y0 - next.y1
            base = 0.15 * curSize
            difference = 0.58 * curSize
            # spacing of 1
            if between > base - 1 and between < base + 1:
                if spacing == 0:
                    spacing = 1
                elif spacing != 1:
                    return -1
            # spacing of 1.5
            elif between > base + difference - 1 and between < base + difference + 1:
                if spacing == 0:
                    spacing = 1.5
                elif spacing != 1.5:
                    return -1
            # spacing of 2
            elif (
                between > base + 2 * difference - 1
                and between < base + 2 * difference + 1
            ):
                if spacing == 0:
                    spacing = 2
                elif spacing != 2:
                    return -1
            # spacing of 2.5
            elif (
                between > base + 3 * difference - 1
                and between < base + 3 * difference + 1
            ):
                if spacing == 0:
                    spacing = 2.5
                elif spacing != 2.5:
                    return -1
            # spacing of 3
            elif (
                between > base + 4 * difference - 1
                and between < base + 4 * difference + 1
            ):
                if spacing == 0:
                    spacing = 3
                elif spacing != 3:
                    return -1
            else:
                return -1
        return spacing

    # Title must be at least three lines that are made into an inverted pyramid and double spaced
    def check_title_format_incorrect(self):
        self.unpack()

        byInfo = self._check_by()
        if byInfo["found_location"] == -1:
            return True

        lineArray = []
        lineWidth = 0
        for text in self._first_page_contents[: byInfo["found_location"]]:
            for line in text:
                if line.get_text().strip() == "":
                    if len(lineArray) > 0:
                        break
                else:
                    if lineWidth == 0:
                        lineWidth = line.x1 = line.x0
                    else:
                        newLineWidth = line.x1 - line.x0
                        if newLineWidth > lineWidth:
                            return True
                        lineWidth = newLineWidth
                    lineArray.append(line)
        return self._check_line_spacing(lineArray) != 2 or len(lineArray) != 3

    # 2 double spaces beneath title
    def check_spacing_beneath_title_incorrect(self):
        self.unpack()

        byInfo = self._check_by()
        if byInfo["found_location"] == -1:
            return True

        for text in reversed(self._first_page_contents[: byInfo["found_location"]]):
            for line in text:
                if line.get_text().strip() != "":
                    between = (
                        line.y0 - self._first_page_contents[byInfo["found_location"]].y1
                    )
                    size = line.y1 - line.y0
                    base = 0.15 * size
                    difference = 0.58 * size
                    calculatedSpace = 3 * (base + 2 * difference) + 2 * size
                    return (
                        between < calculatedSpace - 3 or between > calculatedSpace + 3
                    )
        return True

    # "by" is in all lowercase in the title page
    def check_by_not_lowercase(self):
        self.unpack()

        byInfo = self._check_by()
        return byInfo["found_location"] == -1 or not byInfo["correct_format"]

    # There cannot be two co-chairs; one must be a chair and one is a co-chair
    # Checks for one appearence of "chair" and not more than one appearence of "co-chair"
    def check_chair_requirement_incorrect(self):
        self.unpack()

        numChairs = 0
        numCoChairs = 0
        for text in self._first_page_contents:
            numChairs += text.get_text().strip().lower().count("committee chair")
            numCoChairs += text.get_text().strip().lower().count("co-chair")
        return numChairs != 1 or numCoChairs > 1

    # Correct department listed
    # Checks for "the Department of"
    def check_department_incorrect(self):
        self.unpack()

        for text in self._first_page_contents:
            if "the department of" in text.get_text().strip().lower():
                return False
        return True

    # TUSCALOOSA, ALABAMA in all caps with ALABAMA spelled out
    def check_location_requirement_incorrect(self):
        self.unpack()

        for text in self._first_page_contents:
            if text.get_text().strip() == "TUSCALOOSA, ALABAMA":
                return False
        return True

    # Year of graduation, not year of submission, at bottom of the page
    # Checks for year at the bottom of page
    def check_graduation_year_incorrect(self):
        self.unpack()

        for text in reversed(self._first_page_contents):
            if text.get_text().strip() != "":
                return not text.get_text().strip().isdigit()
        return True

    # Returns student fname and lname
    # if 'by' or the name is not found, return false
    def get_student_name(self):
        self.unpack()

        byInfo = self._check_by()

        if byInfo["found_location"] != -1:
            for text in self._first_page_contents[byInfo["found_location"] + 1 :]:
                if text.get_text().strip() != "":
                    name = text.get_text().strip().split()
                    lname = name[len(name) - 1]
                    fname = " ".join(name[: len(name) - 1])
                    return {"fname": fname, "lname": lname}
        return False

    # Returns if document is a thesis or dissertation
    # if neiter is found, return false
    def get_paper_type(self):
        self.unpack()

        for text in self._first_page_contents:
            if "dissertation" in text.get_text().strip().lower():
                return "dissertation"
            if "thesis" in text.get_text().strip().lower():
                return "thesis"
        return False

    # MARK: Check Copyright Page Requirements

    # find and return the copyright page
    #   Returns the page that the copyright is on
    #   Returns none if copyright is not found
    def _find_copyright_page(self):
        self.unpack()
        for page in self._pages:
            for element in page:
                if isinstance(element, LTTextContainer):
                    for line in element:
                        text = line.get_text().strip().lower()
                        if text != '':
                            if 'copyright' in text:
                                return list(page)
                            else:
                                break
                    else:
                        continue
                    break
        return None # should throw/ display error that copyright page cannont be found


    # Single space between name/copyright notice and "ALL RIGHTS RESERVED"
    def check_spacing_copyright_incorrect(self):
        self.unpack()
        copyrightPage = self._find_copyright_page()

        # make sure a copyright page is found
        if copyrightPage == None:
            return True
        
        copyright_line = None
        all_rights_reserved_line = None

        for element in copyrightPage:
            if isinstance(element, LTTextContainer):
                for line in element:
                    text =  line.get_text().strip().lower()
                    if copyright_line == None and 'copyright' in text:
                        copyright_line = line
                    elif all_rights_reserved_line == None and 'all rights reserved' in text:
                        all_rights_reserved_line = line
        if copyright_line == None and copyright_line == None:
            return True
        return self._check_line_spacing([copyright_line, all_rights_reserved_line]) != 1


    # MARK: Check Abstract Page Requirements

    # find and return the abstract page(s)
    #   Returns array of pages that the abstract is on
    #   Returns none if abstract is not found
    def _find_abstract_page(self):
        self.unpack()

        abstract = []

        for page in self._pages:
            for element in page:
                if isinstance(element, LTTextContainer):
                    for line in element:
                        text = line.get_text().strip().lower()
                        if 'dedication' == text or 'list of abbreviations and symbols' == text or 'aknowledgements' == text or 'contents' == text:
                                return abstract
                        elif len(abstract) > 0 or text =='abstract':
                            abstract.append(page)
                            break
                    else:
                        continue
                    break
        return None # should throw/ display error that abstract page cannont be found

    # Must be double spaced and must not exceed 350-word limit
    def check_abstract_spacing_and_word_limit_incorrect(self):
        self.unpack()

        abstract = self._find_abstract_page()
        if abstract == None:
            return True
        
        abstractText = ''

        for page in abstract:
            lineArray = []
            for element in page:
                if isinstance(element, LTTextContainer):
                    for line in element:
                        text = line.get_text().strip().lower()
                        if text != '' and text != 'abstract':
                            lineArray.append(line)
                            abstractText += ' ' + text
            if self._check_line_spacing(lineArray) != 2:
                return True
        return len(abstractText.split()) > 360


    # Do not include graphs, charts, tables, or other illustrations in the abstract
    def check_charts_in_abstract(self):
        self.unpack()
        abstract = self._find_abstract_page()
        if abstract == None:
            return True

        for page in abstract:
            for element in page:
                if not isinstance(element, LTTextContainer):
                    return True
        return False

    def get_file_name(self):
        return self._file_name
