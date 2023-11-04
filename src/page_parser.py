# %pip install pdfminer.six
import pdfminer.high_level as pdf_hl
import pdfminer.layout as pdf_layout
import os
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import io
import re
import PIL
from PIL import Image
from PIL import ImageDraw


DO_IMAGE = True
NEED_RENDER = False
DO_TEST = True


def mirror_bbox_vertical(bbox, height):
    x0, y0, x1, y1 = bbox
    return (x0, height - y1, x1, height - y0)


def mix_col(c1, c2, alpha):
    c1_a = c1[3] / 255
    c2_a = c2[3] / 255
    tot_a = min(c1_a + c2_a, 1)
    c1_t = tuple([c1[i] * c1[3] / 255 for i in range(3)])
    c2_t = tuple([c2[i] * c2[3] / 255 for i in range(3)])
    c_t = tuple(
        [(c1_t[i] * alpha + c2_t[i] * (1 - alpha)) for i in range(3)] + [tot_a * 255]
    )
    return tuple([int(c_t[i]) for i in range(4)])


def recursive_dict_add(d1, d2):
    for k, v in d2.items():
        if k in d1:
            if type(d1[k]) is dict:
                recursive_dict_add(d1[k], v)
            else:
                d1[k] += v
        else:
            d1[k] = v


class Page_Parser:
    def __init__(self, page: pdf_layout.LTPage):
        self.page: pdf_layout.LTPage = page
        self.unpacked: bool = False
        self.bbox: tuple = page.bbox
        self.width: int = page.width
        self.height: int = page.height
        self.grid = [
            [(255, 255, 255, 255) for _ in range(self.width)]
            for _ in range(self.height)
        ]
        self.bboxes: list[tuple] = []
        self.bbox_contents = []
        self.all_fontdata = []
        self.all_fontnames = {}
        self.all_sizes = {}
        self.content_bbox: None | tuple = (
            None  # The smallest box that contains all the content
        )
        self.color_enums: dict[str, tuple] = {
            "red": (255, 0, 0, 255),
            "green": (0, 255, 0, 255),
            "blue": (0, 0, 255, 255),
            "white": (255, 255, 255, 255),
            "black": (0, 0, 0, 255),
            "yellow": (255, 255, 0, 255),
            "cyan": (0, 255, 255, 255),
            "magenta": (255, 0, 255, 255),
            "transparent_red": (255, 0, 0, 100),
            "transparent_green": (0, 255, 0, 100),
            "transparent_blue": (0, 0, 255, 100),
            "transparent_white": (255, 255, 255, 100),
            "transparent_black": (0, 0, 0, 100),
            "transparent_yellow": (255, 255, 0, 100),
            "transparent_cyan": (0, 255, 255, 100),
            "transparent_magenta": (255, 0, 255, 100),
        }
        self.textbox_types = [
            pdf_layout.LTTextBox,
            pdf_layout.LTTextBoxHorizontal,
            pdf_layout.LTTextBoxVertical,
        ]
        self.text_line_types = [
            pdf_layout.LTTextLine,
            pdf_layout.LTTextLineHorizontal,
            pdf_layout.LTTextLineVertical,
        ]
        self.text_types = [pdf_layout.LTChar]
        self.raw_text = None

    def content_bbox_extend(self, x: int, y: int):
        if self.content_bbox is None:
            self.content_bbox = (x, y, x, y)
        else:
            x0, y0, x1, y1 = self.content_bbox
            self.content_bbox = (min(x0, x), min(y0, y), max(x1, x), max(y1, y))

    def fill(self, x: int, y: int, color: tuple | None = None):
        if x < 0:
            x = 0
        elif x >= self.width:
            x = self.width - 1
        if y < 0:
            y = 0
        elif y >= self.height:
            y = self.height - 1
        if color is None:
            color = (255, 0, 0, 255)
        color: tuple
        if color[3] == 0:
            return
        elif color[3] < 255:
            self.grid[y][x] = mix_col(self.grid[y][x], color, color[3] / 255)
        else:
            self.grid[y][x] = color
        self.content_bbox_extend(x, y)

    def fill_line(self, x0: int, y0: int, x1: int, y2: int, color: tuple | None = None):
        start: tuple = (x0, y0)
        end: tuple = (x1, y2)
        distVec: tuple = (end[0] - start[0], end[1] - start[1])
        dist: float = max((distVec[0] ** 2 + distVec[1] ** 2) ** 0.5, 1)
        distVec: tuple[float, float] = (distVec[0] / dist, distVec[1] / dist)
        for i in range(int(dist + 1)):
            self.fill(
                int(start[0] + i * distVec[0]), int(start[1] + i * distVec[1]), color
            )

    def round_bbox(self, bbox: tuple) -> tuple:
        # Want to round the bbox to the nearest pixels
        # print(bbox)
        x0, y0, x1, y1 = bbox
        x0 = int(x0)
        y0 = int(y0)
        x1 = int(x1)
        y1 = int(y1)
        return (x0, y0, x1, y1)

    def fill_bbox(
        self, bbox: tuple, color: tuple | None = None, fillColor: tuple | None = None
    ):
        if color is None:
            color = (255, 0, 0, 255)
        color: tuple
        x0, y0, x1, y1 = self.round_bbox(bbox)
        top = min(y0, y1)
        bottom = max(y0, y1)
        height = bottom - top
        left = min(x0, x1)
        right = max(x0, x1)
        width = right - left
        # Some computational cleanup, we don't want to render the boxes and such outside of debug
        if NEED_RENDER:
            self.fill_line(left, top, right, top, color)
            self.fill_line(left, bottom, right, bottom, color)
            self.fill_line(left, top, left, bottom, color)
            self.fill_line(right, top, right, bottom, color)
            if height > 1 and width > 1:
                if fillColor is None:
                    fillColor = (color[0], color[1], color[2], 100)
                fillColor: tuple
                for x in range(left + 1, right):
                    for y in range(top + 1, bottom):
                        self.fill(x, y, fillColor)
        else:
            # fill the corners only
            self.fill(left, top, color)
            self.fill(right, top, color)
            self.fill(left, bottom, color)
            self.fill(right, bottom, color)

    def mirror_bbox_vertical(self, bbox: tuple) -> tuple:
        return mirror_bbox_vertical(bbox, self.height)

    def get_fontdata(self, page_content: pdf_layout.LTComponent) -> dict:
        # We are passed some component, we want to recursively check children for font data
        # print(f"Type: {type(page_content)}")
        fontdata = {}
        if type(page_content) in self.textbox_types:
            for child in page_content:
                recursive_dict_add(fontdata, self.get_fontdata(child))
        elif type(page_content) in self.text_line_types:
            for child in page_content:
                recursive_dict_add(fontdata, self.get_fontdata(child))
        elif type(page_content) in self.text_types:
            if hasattr(page_content, "fontname"):
                if "fontname" not in fontdata:
                    fontdata["fontname"] = {page_content.fontname: 1}
                elif page_content.fontname not in fontdata["fontname"]:
                    fontdata["fontname"][page_content.fontname] = 1
                else:
                    fontdata["fontname"][page_content.fontname] += 1
                # print(f"Fontname: {page_content.fontname}")
            if hasattr(page_content, "fontsize"):
                if "fontsize" not in fontdata:
                    fontdata["fontsize"] = {int(page_content.fontsize + 0.5): 1}
                elif page_content.fontsize not in fontdata["fontsize"]:
                    fontdata["fontsize"][int(page_content.fontsize + 0.5)] = 1
                else:
                    fontdata["fontsize"][int(page_content.fontsize + 0.5)] += 1
            if hasattr(page_content, "size"):
                if "size" not in fontdata:
                    fontdata["size"] = {int(page_content.size + 0.5): 1}
                elif page_content.size not in fontdata["size"]:
                    fontdata["size"][int(page_content.size + 0.5)] = 1
                else:
                    fontdata["size"][int(page_content.size + 0.5)] += 1
        return fontdata

    def data_push_fontsize(self, fontdata: dict):
        if "fontsize" in fontdata:
            for size, num in fontdata["fontsize"].items():
                if size not in self.all_sizes:
                    self.all_sizes[size] = num
                else:
                    self.all_sizes[size] += num
        elif "size" in fontdata:
            for size, num in fontdata["size"].items():
                if size not in self.all_sizes:
                    self.all_sizes[size] = num
                else:
                    self.all_sizes[size] += num

    def data_push_fontname(self, fontdata: dict):
        if "fontname" in fontdata:
            for name, num in fontdata["fontname"].items():
                if name not in self.all_fontnames:
                    self.all_fontnames[name] = num
                else:
                    self.all_fontnames[name] += num

    def add_bbox(
        self, bbox: tuple, color: tuple | None = None, fillColor: tuple | None = None
    ):
        self.bboxes.append(bbox)
        self.fill_bbox(bbox, color, fillColor)

    def add_bbox_content(
        self, text: str | None, color: tuple | None = None, fontdata: dict | None = None
    ):
        # bbox already added with add_bbox
        self.bbox_contents.append({"text": text, "color": color, "fontdata": fontdata})

    def push_content(
        self,
        page_content: pdf_layout.LTComponent,
        outlineColor: tuple | None = None,
        fillColor: tuple | None = None,
        textColor: tuple | None = None,
    ):
        bbox = page_content.bbox
        bbox = self.mirror_bbox_vertical(bbox)
        self.add_bbox(bbox, outlineColor, fillColor)
        fontdata = None
        if type(page_content) in self.textbox_types:
            text = page_content.get_text()
            # print(f"BBox {len(self.bboxes)} has text")
            # get font data
            fontdata = self.get_fontdata(page_content)
            if fontdata not in self.all_fontdata:
                self.all_fontdata.append(fontdata)
            self.data_push_fontname(fontdata)
            self.data_push_fontsize(fontdata)
        else:
            # print(f"Type: {type(page_content)}")
            text = None
        self.add_bbox_content(text, textColor, fontdata)

    def filled_ratio(self, ratio) -> bool:
        width = self.width
        height = self.height
        area = width * height
        if self.content_bbox == (None):
            return False
        c_width = self.content_bbox[2] - self.content_bbox[0]
        c_height = self.content_bbox[3] - self.content_bbox[1]
        c_area = c_width * c_height
        if c_area / area < ratio:
            return False
        return True

    def get_raw_text(self, *args, **kwargs):
        if self.raw_text is None:
            self.page: pdf_layout.LTPage
            # self.raw_text = self.page
            self.raw_text = self._recurs_extract_text(self.page)
        return self.raw_text

    def get_char_count(self):
        return len(self.get_raw_text())

    def draw(
        self, bbox_cmp=False, content_bbox=False, *args, **kwargs
    ) -> PIL.Image.Image:
        if not DO_IMAGE:
            return None
        img = Image.new("RGBA", (self.width, self.height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        for x in range(self.width):
            for y in range(self.height):
                draw.point((x, y), fill=self.grid[y][x])
        if bbox_cmp:
            for bbox in self.bboxes:
                draw.rectangle(bbox, outline=(0, 0, 0, 255))
        if content_bbox:
            draw.rectangle(self.content_bbox, outline=(0, 255, 0, 255))
        return img

    def save(self, filename, *args, **kwargs):
        self.draw(*args, **kwargs).save(filename)

    def unpack_page(self):
        if self.unpacked:
            return
        for box in self.page:
            outlineCol = self.color_enums["red"]
            fillCol = self.color_enums["transparent_red"]
            textCol = self.color_enums["black"]
            self.push_content(box, outlineCol, fillCol, textCol)
        self.unpacked = True

    def is_bold(self, font_name):
        bold_indicators = [
            "Bold",
            "Bd",
            "Demi",
            "Black",
            "Heavy",
            "Fat",
            "ExtraBold",
            "ExBold",
            "UltraBold",
            "Super",
            "Strong",
            "Solid",
            "Thick",
            "Fett",
            "Grassetto",
            "Negrita",
            "Medium",
        ]

        # Convert the font name to lower case to ensure case-insensitive comparison
        font_name_lower = font_name.lower()

        # Check if any of the bold indicators are in the font name
        return any(
            bold_indicator.lower() in font_name_lower
            for bold_indicator in bold_indicators
        )

    def is_preliminary_page(self, text=None, page_number=None):
        if page_number is None:
            # Page number is not provided, so we assume it is the first page
            if hasattr(self, "page_number"):
                page_number = self.page_number
            else:
                page_number = 1
        if text is None:
            text = self.get_raw_text(self.page)
        if page_number == 1:
            return True

        if page_number == 2:
            return True

        # Check for Roman numeral page numbers
        words = text.split()
        for word in words:
            if is_roman_numeral(word):
                return True

        return False

    def _get_raw_text(self, page_layout):
        """Extract text from a page layout."""
        # CHAD: I think this misses some text when there are subdivided textboxes, like table cells
        # Need to test if this is better or worse than the recursive version
        if self.raw_text is not None:
            return self.raw_text
        texts = []
        for element in page_layout:
            if isinstance(element, LTTextBox) or isinstance(element, LTTextLine):
                texts.append(element.get_text())
        raw_text = " ".join(texts).strip()
        self.raw_text = raw_text
        return raw_text

    def _recurs_extract_text(self, element=None):
        # CHAD: This should get ALL text, but could be slow. Needs to be tested
        if element is None:
            element = self.page
        text = ""
        if type(element) in self.textbox_types:
            for child in element:
                text += self._recurs_extract_text(child)
        elif type(element) in self.text_line_types:
            for child in element:
                text += child.get_text()
        elif type(element) in self.text_types:
            text += element.get_text()
        return text


def is_roman_numeral(s):
    roman_numeral_pattern = "^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
    return re.match(roman_numeral_pattern, s.strip(), re.IGNORECASE) is not None


def extract_text_from_pdf(file_path):
    # Initialize PDFMiner components
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    laparams = LAParams()
    converter = PDFPageAggregator(resource_manager, laparams=laparams)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    # Open the PDF file
    with open(file_path, "rb") as fh:
        # Process each page in the PDF
        for page_number, page in enumerate(
            PDFPage.get_pages(fh, caching=True, check_extractable=True)
        ):
            page_interpreter.process_page(page)
            layout = converter.get_result()
            yield page_number, layout

    # close open handles
    converter.close()
    fake_file_handle.close()


if __name__ == "__main__":
    if DO_TEST:
        output_file_test = False
        get_fontdata_test = False
        is_bold = True
        is_preliminary = True
        if output_file_test:
            # we are in /src, we want to pull pdf from /prototyping
            file = os.path.join(
                os.path.dirname(__file__), "..", "prototyping", "Homework_1.pdf"
            )
            output = pdf_hl.extract_pages(file)
            # output = pdf_hl.extract_pages("Homework_1.pdf")
            # print(output)
            output = list(output)

            page_handlers = []
            for page in output:
                page_handlers.append(Page_Parser(page))
            for ind, page in enumerate(page_handlers):
                page: Page_Parser
                page.unpack_page()
                img_filename = f"page_{ind}.png"
                path_filename = os.path.join(
                    os.path.dirname(__file__), "..", "output_files", img_filename
                )
                page.save(
                    path_filename, bbox_cmp=False, content_bbox=True, draw_text=True
                )

        if get_fontdata_test:
            # we are in /src, we want to pull pdf from /prototyping
            file = os.path.join(
                os.path.dirname(__file__), "..", "prototyping", "Homework_1.pdf"
            )
            output = pdf_hl.extract_pages(file)
            output = list(output)

            page_handlers = []
            for page in output:
                page_handlers.append(Page_Parser(page))

            all_fontnames = {}
            all_sizes = {}

            for ind, page in enumerate(page_handlers):
                page: Page_Parser
                page.unpack_page()
                print(f"Page {ind}")
                # print(page.all_fontdata)
                print(page.all_fontnames)
                print(page.all_sizes)
                print()
                recursive_dict_add(all_fontnames, page.all_fontnames)
                recursive_dict_add(all_sizes, page.all_sizes)

            print("All fontnames:")
            print(all_fontnames)
            print()
            print("All sizes:")
            print(all_sizes)
            print()

        if is_preliminary:
            file = os.path.join(
                os.path.dirname(__file__),
                "..",
                "prototyping",
                "example_thesis_caroline.pdf",
            )
            output = pdf_hl.extract_pages(file)
            output = list(output)

            for page_number, layout in enumerate(output):
                page = Page_Parser(layout)
                raw_text = page.get_raw_text(layout)

                # Check if the current page is a preliminary page
                if page.is_preliminary_page(raw_text, page_number + 1):
                    print(f"Page {page_number + 1} is a preliminary page.")
                else:
                    print(f"Page {page_number + 1} is not a preliminary page.")

        if is_bold:
            file = os.path.join(
                os.path.dirname(__file__),
                "..",
                "prototyping",
                "example_thesis_caroline.pdf",
            )
            output = pdf_hl.extract_pages(file)
            output = list(output)

            for ind, page_layout in enumerate(output):
                page = Page_Parser(page_layout)
                page.unpack_page()
                raw_text = page.get_raw_text(page_layout)

                # Check if the current page is a preliminary page
                if page.is_preliminary_page(raw_text, ind + 1):
                    for fontname in page.all_fontnames:
                        if page.is_bold(fontname):
                            print(f"On preliminary page {ind + 1}, {fontname} is bold")
                        else:
                            print(
                                f"On preliminary page {ind + 1}, {fontname} is not bold"
                            )
                else:
                    print(f"Page {ind + 1} is not a preliminary page")
