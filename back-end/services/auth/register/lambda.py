from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from passlib.hash import pbkdf2_sha256
import boto3
import json
import os

USERS_TABLE = os.environ["USERS_TABLE"]
COGNITO_USER_POOL_ID = os.environ["USER_POOL_ID"]
COGNITO_CLIENT_ID = os.environ["USER_POOL_CLIENT_ID"]
DEFAULT_GROUP = os.environ.get("DEFAULT_GROUP", "LoggedInUser")

dynamodb = boto3.resource("dynamodb")
cognito = boto3.client("cognito-idp")

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        username = body.get("username")
        email = body.get("email")
        password = body.get("password")

        if not username or not email or not password:
            return {"statusCode": 400, "body": json.dumps({"message": "Missing required fields"})}

        table = dynamodb.Table(USERS_TABLE)

        # Check if username/email exists
        existing_username = table.get_item(Key={"user_id": username})
        if "Item" in existing_username:
            return {"statusCode": 409, "body": json.dumps({"message": "Username already exists"})}

        existing_email = table.query(
            IndexName="byEmail",
            KeyConditionExpression=Key("email").eq(email)
        )
        if existing_email.get("Items"):
            return {"statusCode": 409, "body": json.dumps({"message": "Email already exists"})}

        # Hash password
        hashed_password = pbkdf2_sha256.hash(password)

        # Create user in Cognito
        try:
            cognito.admin_create_user(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=username,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "email_verified", "Value": "true"},
                ],
                TemporaryPassword=password,
                MessageAction="SUPPRESS"  # Don't send auto email
            )

            # Set permanent password
            cognito.admin_set_user_password(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=username,
                Password=password,
                Permanent=True
            )

            # Add user to default group
            cognito.admin_add_user_to_group(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=username,
                GroupName=DEFAULT_GROUP
            )

        except ClientError as e:
            return {"statusCode": 500, "body": json.dumps({"message": f"Cognito error: {str(e)}"})}

        # Save user in DynamoDB
        table.put_item(Item={
            "user_id": username,
            "email": email,
            "password": hashed_password,
        })

        return {"statusCode": 201, "body": json.dumps({"message": "User registered successfully"})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": f"Internal server error: {str(e)}"})}
