# %pip install pdfminer.six
import pdfminer
import pdfminer.high_level as pdf_hl
import pdfminer.layout as pdf_layout
import os

DO_IMAGE = True
DO_TEST = True
if DO_IMAGE:
    import PIL
    from PIL import Image
    from PIL import ImageDraw


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


class PagePixGrid:
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

    def content_bbox_extend(self, x: int, y: int):
        if self.content_bbox is None:
            self.content_bbox = (x, y, x, y)
        else:
            x0, y0, x1, y1 = self.content_bbox
            self.content_bbox = (min(x0, x), min(y0, y), max(x1, x), max(y1, y))

    def fill(self, x: int, y: int, color: tuple | None = None):
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

    def mirror_bbox_vertical(self, bbox: tuple) -> tuple:
        return mirror_bbox_vertical(bbox, self.height)

    def get_fontdata(self, page_content: pdf_layout.LTComponent) -> dict:
        # We are passed some component, we want to recursively check children for font data
        # print(f"Type: {type(page_content)}")
        fontdata = {}
        if type(page_content) in self.textbox_types:
            for child in page_content:
                return self.get_fontdata(child)
        elif type(page_content) in self.text_line_types:
            for child in page_content:
                return self.get_fontdata(child)
        elif type(page_content) in self.text_types:
            if hasattr(page_content, "fontname"):
                if not "fontname" in fontdata:
                    fontdata["fontname"] = [page_content.fontname]
                elif not page_content.fontname in fontdata["fontname"]:
                    fontdata["fontname"].append(page_content.fontname)
                # print(f"Fontname: {page_content.fontname}")
            if hasattr(page_content, "fontsize"):
                if not "fontsize" in fontdata:
                    fontdata["fontsize"] = [page_content.fontsize]
                elif not page_content.fontsize in fontdata["fontsize"]:
                    fontdata["fontsize"].append(page_content.fontsize)
            if hasattr(page_content, "size"):
                if not "size" in fontdata:
                    fontdata["size"] = [page_content.size]
                elif not page_content.size in fontdata["size"]:
                    fontdata["size"].append(page_content.size)
        return fontdata

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
            if not fontdata in self.all_fontdata:
                self.all_fontdata.append(fontdata)
        else:
            # print(f"Type: {type(page_content)}")
            text = None
        self.add_bbox_content(text, textColor, fontdata)

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
        # if draw_text:
        #     for i in range(len(self.bboxes)):
        #         content = self.bbox_contents[i]
        #         text = content["text"]
        #         color = content["color"]
        #         fontdata = content["fontdata"]
        #         fontsize = 12
        #         if fontdata is not None and ("fontsize" in fontdata or "size" in fontdata):
        #             if "fontsize" in fontdata:
        #                 fontsize = fontdata["fontsize"]
        #             else:
        #                 fontsize = fontdata["size"]
        #         if fontdata is not None and "fontname" in fontdata:
        #             font = get_font(fontdata["fontname"], fontsize)
        #         else:
        #             font = get_font("", fontsize)
        #         if text is not None:
        #             draw.text(self.bboxes[i][0:2], text, fill = color, font = font)
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


if __name__ == "__main__":
    if DO_TEST:
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
            page_handlers.append(PagePixGrid(page))
        for ind, page in enumerate(page_handlers):
            page: PagePixGrid
            page.unpack_page()
            img_filename = f"page_{ind}.png"
            path_filename = os.path.join(
                os.path.dirname(__file__), "..", "output_files", img_filename
            )
            page.save(path_filename, bbox_cmp=False, content_bbox=True, draw_text=True)
