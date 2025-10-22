from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from passlib.hash import pbkdf2_sha256
from general_utils import response
import boto3, json, os, uuid

USERS_TABLE = os.environ["USERS_TABLE"]
COGNITO_USER_POOL_ID = os.environ["USER_POOL_ID"]
DEFAULT_GROUP = os.environ.get("DEFAULT_GROUP", "User")
CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))

dynamodb = boto3.resource("dynamodb")
cognito = boto3.client("cognito-idp")


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        username = body.get("username")
        email = body.get("email")
        password = body.get("password")
        first_name = body.get("first_name")
        last_name = body.get("last_name")
        birthday = body.get("birthday")
        user_id = f"USER~{uuid.uuid4()}"

        if not username or not email or not password or not first_name or not last_name or not birthday:
            return response(400, error="Missing required fields")

        table = dynamodb.Table(USERS_TABLE)

        # Check if username/email exists
        if table.get_item(Key={"user_id": username}).get("Item"):
            return response(409, error="Username already exists")

        if table.query(IndexName="byEmail", KeyConditionExpression=Key("email").eq(email)).get("Items"):
            return response(409, error="Email already exists")

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
                    {"Name": "given_name", "Value": first_name},
                    {"Name": "family_name", "Value": last_name},
                    {"Name": "birthdate", "Value": birthday},  # Make sure format is YYYY-MM-DD
                    {"Name": "custom:userId", "Value": user_id}
                ],
                MessageAction="SUPPRESS"
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
            code = e.response.get("Error", {}).get("Code", "UnknownError")
            return response(500, error=f"Cognito error ({code}): {str(e)}")

        table.put_item(Item={
            "user_id": username,
            "email": email,
            "password": hashed_password,
            "first_name": first_name,
            "last_name": last_name,
            "birthday": birthday
        })

        return response(201, error="User registered successfully")

    except Exception as e:
        return response(500, error=f"Internal server error: {str(e)}")
