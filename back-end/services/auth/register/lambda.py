from botocore.exceptions import ClientError
from general_utils import response
from create import create_user
import boto3, json, os, uuid

COGNITO_USER_POOL_ID = os.environ["USER_POOL_ID"]
DEFAULT_GROUP = os.environ.get("DEFAULT_GROUP", "User")
cognito = boto3.client("cognito-idp")


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        username = body.get("username")
        email = body.get("email")
        password = body.get("password")
        name = body.get("first_name")
        surname = body.get("last_name")
        birthday = body.get("birthday")
        user_id = f"USER~{uuid.uuid4()}"

        if not username or not email or not password:
            return response(400, error="Missing required fields")

        try:
            cognito.admin_get_user(UserPoolId=COGNITO_USER_POOL_ID, Username=username)
            return response(409, error="Username already exists")
        except cognito.exceptions.UserNotFoundException:
            pass

        resp = cognito.list_users(UserPoolId=COGNITO_USER_POOL_ID, Filter=f'email = "{email}"')
        if resp["Users"]:
            return response(409, error="Email already exists")

        user_attributes = [
            {"Name": "email", "Value": email},
            {"Name": "email_verified", "Value": "true"},
            {"Name": "custom:userId", "Value": user_id}
        ]

        if name: user_attributes.append({"Name": "given_name", "Value": name})
        if surname: user_attributes.append({"Name": "family_name", "Value": surname})
        if birthday: user_attributes.append({"Name": "birthdate", "Value": birthday})  # format is YYYY-MM-DD

        try:
            cognito.admin_create_user(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=username,
                UserAttributes=user_attributes,
                MessageAction="SUPPRESS"
            )

            cognito.admin_set_user_password(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=username,
                Password=password,
                Permanent=True
            )

            cognito.admin_add_user_to_group(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=username,
                GroupName=DEFAULT_GROUP
            )

        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "UnknownError")
            return response(500, error=f"Cognito error ({code}): {str(e)}")

        create_user(user_id, name, surname, email, birthday)
        return response(201, error="User registered successfully")

    except Exception as e:
        return response(500, error=f"Internal server error: {str(e)}")
