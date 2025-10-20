from botocore.exceptions import ClientError
import boto3, json, os

CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))
COGNITO_USER_POOL_ID = os.environ["USER_POOL_ID"]
cognito = boto3.client("cognito-idp")


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        access_token = body.get("access_token")

        if not access_token:
            return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Access token required"})}

        try:
            cognito.global_sign_out(AccessToken=access_token)
        except cognito.exceptions.NotAuthorizedException:
            return {"statusCode": 401, "headers": CORS_HEADERS, "body": json.dumps({"message": "Invalid or expired access token"})}
        except ClientError as e:
            return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"message": f"Cognito error: {str(e)}"})}

        return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"message": "Logout successful"})}

    except Exception as e:
        return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"message": f"Internal server error: {str(e)}"})}
