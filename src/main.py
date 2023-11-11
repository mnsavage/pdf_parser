import os
import boto3
from botocore.exceptions import ClientError


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
