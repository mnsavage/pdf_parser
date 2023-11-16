import os
import boto3
from botocore.exceptions import ClientError
from pdf_parser import Pdf_Parser


def get_pdf_requirements_validation(pdf):
    parser = Pdf_Parser(pdf)

    name = parser.get_student_name()
    if name is False:
        name.fname = "could_not_find_name"
        name.lname = "error"

    paperType = parser.get_paper_type()
    if paperType is False:
        paperType == "could_not_find_paper_type"

    pdf_requirments = {
        "name": parser.get_file_name(),
        "newName": f"{name.lname}.{name.fname}.{paperType}",
        "fname": name.fname,
        "lname": name.lname,
        "header": [
            {
                "title": "Document Formatting",
                "requirements": [
                    {"title": "File format: PDF", "met": True},
                    {
                        "title": "File name must use only English letters, underscore lines, and Arabic numbers with no spaces in the file name ",
                        "met": None,
                    },
                ],
            },
            {
                "title": "Page Formatting & Font",
                "requirements": [
                    {
                        "title": 'Check margins: 1" on the left, 1" on the right and bottom. 2" top margin to begin each major section like preliminary pages, chapters, title page, and references; 1" top margin for all other pages',
                        "met": parser.margin_check(72, 72),
                    },
                    {
                        "title": "Line spacing: The body text must be double spaced with no extra spaces between paragraphs",
                        "met": None,
                    },
                    {
                        "title": "Line spacing: Footnotes, bibliographic entries, long quoted passages, etc. should be single spaced",
                        "met": None,
                    },
                    {
                        "title": "Font: Use a standard 12-point font consistently throughout the document, including headings and subheadings, and must be black font including URLs.",
                        "met": parser.check_font_size_not_same_throughout_pdf(),
                    },
                    {
                        "title": "There should be no bold font on preliminary pages",
                        "met": parser.check_bold_in_preliminary_pages(),
                    },
                    {
                        "title": "Justification: left justification throughout the document and for page number entries in CONTENTS and LISTS, the page numbers should be right aligned.",
                        "met": None,
                    },
                    {
                        "title": 'Remove "orphans" (headings or sub-headings located at the bottom of a page that is not followed by text) and "widows" (short lines ending a paragraph at the top of the page)',
                        "met": None,
                    },
                    {
                        "title": "No Blank pages in the document",
                        "met": parser.check_no_empty_pages()
                        or parser.check_font_not_same_throughout_pdf(),
                    },
                    {
                        "title": "Pagination: Numbers must be positioned 0.5 inches from the bottom of the page and centered",
                        "met": None,
                    },
                    {
                        "title": "Pagination: Numbers must correspond with the Table of Contents and any List Pages",
                        "met": None,
                    },
                    {
                        "title": "Pagination: Page numbers cannot be bolded and must be the same font size and same font type as general document.",
                        "met": None,
                    },
                    {
                        "title": "Pagination Roman numerals: Do not use page numbers before the ABSTRACT page Begin with p. ii on the ABSTRACT page and continue with all pages following until the first page of the text",
                        "met": None,
                    },
                    {
                        "title": "Pagination Arabic numerals: Begin Arabic numerals with p. 1 on the first page of the body text",
                        "met": None,
                    },
                    {"title": "Other: see comments", "met": None},
                ],
            },
            {
                "title": "Page Order & Section Formatting",
                "requirements": [
                    {
                        "title": "Title page: Title must be at least three lines that are made into an inverted pyramid and double spaced",
                        "met": parser.check_title_format_incorrect(),
                    },
                    {
                        "title": "Title page: 2 double spaces beneath title",
                        "met": parser.check_spacing_beneath_title_incorrect(),
                    },
                    {
                        "title": 'Title page: "by" is in all lowercase',
                        "met": parser.check_by_not_lowercase(),
                    },
                    {
                        "title": "Title page: There cannot be two co-chairs; one must be a chair and one is a co-chair",
                        "met": parser.check_chair_requirement_incorrect,
                    },
                    {
                        "title": "Title page: Correct department listed",
                        "met": parser.check_department_incorrect(),
                    },
                    {
                        "title": "Title page: TUSCALOOSA, ALABAMA in all caps with ALABAMA spelled out",
                        "met": parser.check_location_requirement_incorrect(),
                    },
                    {
                        "title": "Title page: Year of graduation, not year of submission, at bottom of the page",
                        "met": parser.check_graduation_year_incorrect(),
                    },
                    {
                        "title": 'Copyright Page: Single space between name/copyright notice and "ALL RIGHTS RESERVED"',
                        "met": parser.check_spacing_copyright_incorrect(),
                    },
                    {
                        "title": "Abstract: Must be double spaced and must not exceed 350-word limit",
                        "met": parser.check_abstract_spacing_and_word_limit_incorrect(),
                    },
                    {
                        "title": "Abstract: Do not include graphs, charts, tables, or other illustrations in the abstract",
                        "met": parser.check_charts_in_abstract(),
                    },
                    {
                        "title": "Abstract: Include no more than 6 keywords or key phrases at the end of the abstract",
                        "met": None,
                    },
                    {"title": "Dedication page: optional", "met": None},
                    {
                        "title": "List of abbreviations and symbols: mandatory if the document has abbreviations and symbols",
                        "met": None,
                    },
                    {"title": "Acknowledgments", "met": None},
                    {
                        "title": "Contents: Must include each of the preliminary pages except title and copyright page with correct page numbers",
                        "met": None,
                    },
                    {
                        "title": "Contents: Headings/subheadings should be indented hierarchically. Also the headings/subheadings/chapter titles must match exactly between CONTENTS and the general document, i.e. punctuation, capitalization, numbering (if any used) and spelling",
                        "met": None,
                    },
                    {
                        "title": "Contents: All references must be at the end of the document but before Appendices",
                        "met": None,
                    },
                    {
                        "title": "Contents: All page numbers should be right justified on the margin ",
                        "met": None,
                    },
                    {
                        "title": "Contents: All entries longer than one line must be single spaced but maintain double spaces between separate entries",
                        "met": None,
                    },
                    {
                        "title": "Contents: The text should not run over the page numbers",
                        "met": None,
                    },
                    {
                        "title": "Contents: Use leaders (the multiple periods)",
                        "met": None,
                    },
                    {
                        "title": "Contents: No italicization or bolding in CONTENTS",
                        "met": None,
                    },
                    {
                        "title": "Contents: Should be CONTENTS and not TABLE OF CONTENTS",
                        "met": None,
                    },
                    {
                        "title": "List of figures: Must include the figure number, exact title, and figure page number",
                        "met": None,
                    },
                    {
                        "title": "List of figures: All entries longer than one line must be single spaced but maintain double spaces between separate entries",
                        "met": None,
                    },
                    {
                        "title": "List of figures: The text should not run over the page numbers",
                        "met": None,
                    },
                    {
                        "title": "List of Additional Files, i.e. LIST OF SCHEMES: required only if additional files are included",
                        "met": None,
                    },
                    {
                        "title": "Text: Must be divided into chapters/sections",
                        "met": None,
                    },
                    {
                        "title": "Text: Include materials that are independent of but relevant to the text (ex. surveys, additional data, computer printouts)",
                        "met": None,
                    },
                    {
                        "title": "Text: Must conform to rules for margins, but print may be reduced in size",
                        "met": None,
                    },
                    {
                        "title": 'Text: Each major section like separate chapters must begin with a 2" top margin',
                        "met": None,
                    },
                    {
                        "title": "References: Cannot split one reference on to two pages",
                        "met": None,
                    },
                    {"title": "References: All URLs must be in black ink", "met": None},
                    {
                        "title": 'References: Begin the first page of REFERENCES with a 2" top margin',
                        "met": None,
                    },
                    {"title": "Appendices: Optional", "met": None},
                    {"title": "Other: see comments", "met": None},
                ],
            },
            {
                "title": "Tables & Figures",
                "requirements": [
                    {
                        "title": "Table/figure placement: Tables/figures may not be grouped at the end of the dissertation",
                        "met": True,
                    },
                    {
                        "title": "Table/figure headings: Table headings must be positioned above the table using the same font style and size as used in the main body text ",
                        "met": None,
                    },
                    {
                        "title": 'Table/figure headings: Do not abbreviate the word "figure"',
                        "met": None,
                    },
                    {
                        "title": "Table/figure headings: Place page numbers in portrait position for landscaped pages",
                        "met": None,
                    },
                    {
                        "title": "For landscaped tables/figures, headings placed on the same page must be in landscape orientation to match the table/figure ",
                        "met": None,
                    },
                    {"title": "Other: see comments", "met": None},
                ],
            },
            {
                "title": "Signatures",
                "requirements": [
                    {
                        "title": "Do not reproduce signatures in electronic theses/dissertations",
                        "met": None,
                    },
                    {"title": "Other: see comments", "met": None},
                ],
            },
            {
                "title": "IRB Approval Letters",
                "requirements": [
                    {
                        "title": "If your research has IRB approval letters they must be included as the final appendix (if you have other appendices) and it must be titled and formatted like the other appendices. The CONTENTS must signify what page has the IRB Approval Letters in it",
                        "met": None,
                    },
                    {
                        "title": "All ink signatures and initials are blacked out",
                        "met": None,
                    },
                    {"title": 'Begin with a 2" top margin', "met": None},
                    {"title": "Other: see comments", "met": None},
                ],
            },
            {
                "title": "Miscellaneous",
                "requirements": [
                    {
                        "title": "Security restrictions: do not incorporate restrictions such as prohibiting copy/paste, compression, or password protection",
                        "met": None,
                    },
                    {"title": "Other: see comments", "met": None},
                ],
            },
            {
                "title": "Dissertations Only",
                "requirements": [
                    {
                        "title": "Submit confirmation page: Survey of Earned Doctorates https://sed-ncses.org",
                        "met": None,
                    },
                    {
                        "title": 'Submit above document via "Manage additional files" within your ETD and follow the file naming conventions in the ETD Submission Guide',
                        "met": None,
                    },
                ],
            },
        ],
    }

    return pdf_requirments


def main():
    storage_name = os.getenv("DYNAMODB_NAME", None)
    UUID = os.getenv("DYNAMODB_KEY", None)

    # check if environment variables were retrieve
    if storage_name is None and UUID is None:
        raise ValueError("Environment variables were not retrieve")

    try:
        # Create a DynamoDB client
        dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))

        # Reference the DynamoDB table
        table = dynamodb.Table(storage_name)

        # Key of the item you want to update (replace UUID with your actual uuid value)
        key = {"uuid": UUID}

        # Define new values for job_status and job_output
        new_job_status = "completed"
        new_job_output = "hello world from batch job"

        # Update the 'job_status' and 'job_output' attributes of the item with the given key
        update_expression = "SET job_status = :new_status, job_output = :new_output"
        expression_attribute_values = {
            ":new_status": new_job_status,
            ":new_output": new_job_output,
        }

        # Perform the update operation
        response = table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",  # Returns the new values of the updated attributes
        )

        print(response)

    except ClientError as e:
        print(f"Error: {e.response['Error']['Message']}")

    else:
        print("Updating database was successful")


if __name__ == "__main__":
    main()
