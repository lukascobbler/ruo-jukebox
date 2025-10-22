from botocore.exceptions import ClientError
from general_utils import response
import boto3, json, os

COGNITO_CLIENT_ID = os.environ["USER_POOL_CLIENT_ID"]
cognito = boto3.client("cognito-idp")


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        username = body.get("username")
        password = body.get("password")

        if not username or not password:
            return response(400, error="Username and password required")

        try:
            resp = cognito.initiate_auth(
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": username, "PASSWORD": password}
            )
        except cognito.exceptions.NotAuthorizedException:
            return response(401, error="Invalid username or password")
        except cognito.exceptions.UserNotFoundException:
            return response(404, error="User not found")
        except ClientError as e:
            return response(500, error=f"Cognito error: {str(e)}")

        body = json.dumps({
            "message": "Login successful",
            "id_token": resp["AuthenticationResult"]["IdToken"],
            "access_token": resp["AuthenticationResult"]["AccessToken"],
            "refresh_token": resp["AuthenticationResult"]["RefreshToken"],
            "expires_in": resp["AuthenticationResult"]["ExpiresIn"],
            "token_type": resp["AuthenticationResult"]["TokenType"]
        })

        return response(200, body)

    except Exception as e:
        return response(500, error=f"Internal server error: {str(e)}")
