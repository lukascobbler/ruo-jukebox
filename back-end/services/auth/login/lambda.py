from botocore.exceptions import ClientError
import boto3
import json
import os

COGNITO_CLIENT_ID = os.environ["USER_POOL_CLIENT_ID"]
cognito = boto3.client("cognito-idp")

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        username = body.get("username")
        password = body.get("password")

        if not username or not password:
            return {"statusCode": 400, "body": json.dumps({"message": "Username and password required"})}

        try:
            resp = cognito.initiate_auth(
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": username, "PASSWORD": password}
            )
        except cognito.exceptions.NotAuthorizedException:
            return {"statusCode": 401, "body": json.dumps({"message": "Invalid username or password"})}
        except cognito.exceptions.UserNotFoundException:
            return {"statusCode": 404, "body": json.dumps({"message": "User not found"})}
        except ClientError as e:
            return {"statusCode": 500, "body": json.dumps({"message": f"Cognito error: {str(e)}"})}

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Login successful",
                "id_token": resp["AuthenticationResult"]["IdToken"],
                "access_token": resp["AuthenticationResult"]["AccessToken"],
                "refresh_token": resp["AuthenticationResult"]["RefreshToken"],
                "expires_in": resp["AuthenticationResult"]["ExpiresIn"],
                "token_type": resp["AuthenticationResult"]["TokenType"]
            })
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": f"Internal server error: {str(e)}"})}
