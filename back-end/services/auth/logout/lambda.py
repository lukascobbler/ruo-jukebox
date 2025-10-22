from botocore.exceptions import ClientError
from general_utils import response
import boto3, json, os

CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))
COGNITO_USER_POOL_ID = os.environ["USER_POOL_ID"]
cognito = boto3.client("cognito-idp")


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        access_token = body.get("access_token")

        if not access_token:
            return response(400, error="Access token required")
            return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Access token required"})}

        try:
            cognito.global_sign_out(AccessToken=access_token)
        except cognito.exceptions.NotAuthorizedException:
            return response(401, error="Invalid or expired access token")
        except ClientError as e:
            return response(500, error=f"Cognito error: {str(e)}")

        return response(200, error="Logout successful")

    except Exception as e:
        return response(500, error=f"Internal server error: {str(e)}")
