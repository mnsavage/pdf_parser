import os
import boto3
import base64
import json
from io import BytesIO
from botocore.exceptions import ClientError
from pdf_parser import Pdf_Parser

def get_file_info(pdf):
    parser = Pdf_Parser(pdf)
    first_name, last_name = parser.get_student_name()
    first_name = "could_not_find_name" if first_name is None else first_name
    last_name = "error" if last_name is None else last_name
    paper_type = parser.get_paper_type()
    paper_type = "could_not_find_paper_type" if paper_type is None else paper_type
    new_file_name = f'{last_name}.{first_name}.{paper_type}'


    return first_name, last_name, new_file_name

def handle_pdf_requirements_validation_failure(e, encoded_pdf, file_name, table, key):
        error_message = f"Error message: {e}"

        with open('pdf_validation_output.json', 'r') as file:
            data = json.load(file)
            
        data["name"] = file_name
        
        update_expression = "SET job_status = :new_status, job_output = :new_output"
        expression_attribute_values = {
            ":new_status": e,
            ":new_output": json.dumps(data),
        }
        table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",  # Returns the new values of the updated attributes
        )
        raise Exception(error_message)
    
def upload_successful_pdf_requirements_validation(job_output, table, key):
        update_expression = "SET job_status = :new_status, job_output = :new_output"
        expression_attribute_values = {
            ":new_status": "completed",
            ":new_output": json.dumps(job_output),
        }

        table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",  # Returns the new values of the updated attributes
        )
    
def get_pdf_requirements_validation(pdf, old_file_name):
    """
    Description: creates a dictionary with information about the requirements the pdf passes or not
    """
    parser = Pdf_Parser(pdf)
    first_name, last_name, new_file_name = get_file_info(pdf)



    
    with open('pdf_validation_output.json', 'r') as file:
        data = json.load(file)
        
    #file info
    data["name"] = old_file_name
    data["newName"] = new_file_name
    data["fname"] = first_name
    data["lname"] = last_name
    # Page Formatting & Font
    data["header"][1]["requirements"][0]["met"] = parser.margin_check(72, 72)
    data["header"][1]["requirements"][3]["met"] = parser.check_font_size_not_same_throughout_pdf()
    data["header"][1]["requirements"][4]["met"] = parser.check_bold_in_preliminary_pages()
    data["header"][1]["requirements"][7]["met"] = parser.check_no_empty_pages() or parser.check_font_not_same_throughout_pdf()
    # Page Order & Section Formatting
    data["header"][2]["requirements"][0]["met"] = parser.check_title_format_incorrect()
    data["header"][2]["requirements"][1]["met"] = parser.check_spacing_beneath_title_incorrect()
    data["header"][2]["requirements"][2]["met"] = parser.check_by_not_lowercase()
    data["header"][2]["requirements"][3]["met"] = parser.check_chair_requirement_incorrect()
    data["header"][2]["requirements"][4]["met"] = parser.check_department_incorrect()
    data["header"][2]["requirements"][5]["met"] = parser.check_location_requirement_incorrect()
    data["header"][2]["requirements"][6]["met"] = parser.check_graduation_year_incorrect()
    data["header"][2]["requirements"][7]["met"] = parser.check_spacing_copyright_incorrect()
    data["header"][2]["requirements"][8]["met"] = parser.check_abstract_spacing_and_word_limit_incorrect()
    data["header"][2]["requirements"][9]["met"] = parser.check_charts_in_abstract()
    
    #is pdf and validation work
    data["header"][0]["requirements"][0]["met"] = False
    
    return data


def ensure_base64_padding(encoded_pdf):
    """
    Description: checks for incorrect base64 padding and if exist fixes it
    """
    missing_padding = len(encoded_pdf) % 4
    if missing_padding:
        if isinstance(encoded_pdf, str):
            encoded_pdf += "=" * (4 - missing_padding)
        else:
            raise TypeError(
                f"Expected data to be bytes or string, got {type(encoded_pdf)} instead."
            )

    return encoded_pdf


def convert_encoded_pdf_to_io(encoded_pdf):
    """
    Description: converts a encoded pdf to io for pdfminer library to use
    """
    if isinstance(encoded_pdf, bytes):
        encoded_pdf = encoded_pdf.decode("utf-8")

    encoded_pdf = ensure_base64_padding(encoded_pdf)
    decoded_pdf = base64.b64decode(encoded_pdf)
    pdf_io = BytesIO(decoded_pdf)
    return pdf_io


def main():
    dynamo_name = os.getenv("DYNAMODB_NAME", None)
    s3_name = os.getenv("S3_NAME", None)
    UUID = os.getenv("DYNAMODB_KEY", None)
    file_name = os.getenv("FILE_NAME", None)

    # check if environment variables were retrieve
    if dynamo_name is None and UUID is None:
        raise ValueError("Environment variables were not retrieve")

    # Reference the DynamoDB table
    dynamodb_client = boto3.resource(
        "dynamodb", region_name=os.getenv("AWS_REGION")
    )
    table = dynamodb_client.Table(dynamo_name)

    # Reference s3 object
    s3_client = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
    s3_object = s3_client.get_object(Bucket=s3_name, Key=UUID)

    # Key of the item you want to update (replace UUID with your actual uuid value)
    key = {"uuid": UUID}
    
    try:
        # Define new values for job_status and job_output
        encoded_pdf = s3_object["Body"].read()
        pdf_io = convert_encoded_pdf_to_io(encoded_pdf=encoded_pdf)
        job_output = get_pdf_requirements_validation(
            pdf=pdf_io, old_file_name=file_name
        )

    except ClientError as e: # encoded pdf validation fails
        handle_pdf_requirements_validation_failure(e, encoded_pdf, file_name, table, key)

    else:
        upload_successful_pdf_requirements_validation(job_output, table, key)


if __name__ == "__main__":
    main()
