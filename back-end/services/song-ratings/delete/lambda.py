import os, json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
ratings = dynamodb.Table(os.environ["RATINGS_TABLE"])

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,PUT,DELETE,GET,PATCH,POST",
}

def _claims(event):
    return (event.get("requestContext") or {}).get("authorizer", {}).get("claims", {}) or {}

def _user_id(event):
    return _claims(event).get("sub") or ""

def _error(code, msg):
    return {"statusCode": code, "headers": CORS_HEADERS, "body": json.dumps({"message": msg})}

def lambda_handler(event, context):
    uid = _user_id(event)
    if not uid:
        return _error(401, "Unauthorized")

    sid = ((event.get("pathParameters") or {}).get("id") or "").strip()
    if not sid:
        return _error(400, "Missing song id in path")

    try:
        resp = ratings.delete_item(
            Key={"song_id": sid, "user_id": uid},
            ReturnValues="ALL_OLD"
        )
    except ClientError as e:
        return _error(500, f"Failed to delete rating: {str(e)}")

    if not resp.get("Attributes"):
        return _error(404, "Rating not found")

    return {"statusCode": 204, "headers": CORS_HEADERS, "body": ""}
