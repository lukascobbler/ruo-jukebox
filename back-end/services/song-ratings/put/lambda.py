import os, json, time
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
ratings = dynamodb.Table(os.environ["RATINGS_TABLE"])
songs = dynamodb.Table(os.environ["SONGS_TABLE"])

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,PUT,DELETE,GET,PATCH,POST",
}

def _claims(event):
    return (event.get("requestContext") or {}).get("authorizer", {}).get("claims", {}) or {}

def _user_id(event):
    return _claims(event).get("sub") or ""

def _json(body):
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(body)}

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
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON body")

    val = body.get("value", None)
    if not isinstance(val, int):
        return _error(400, "Field 'value' (int) is required")
    if not (1 <= val <= 5):
        return _error(400, "Rating 'value' must be in [1..5]")

    song = songs.get_item(Key={"song_id": sid}, ProjectionExpression="song_id").get("Item")
    if not song:
        return _error(404, "Song not found")

    now = int(time.time())

    try:
        resp = ratings.update_item(
            Key={"song_id": sid, "user_id": uid},
            UpdateExpression="SET #v = :v, updated_at = :now, created_at = if_not_exists(created_at, :now)",
            ExpressionAttributeNames={"#v": "value"},
            ExpressionAttributeValues={":v": Decimal(val), ":now": now},
            ReturnValues="ALL_OLD",
        )
    except ClientError as e:
        return _error(500, f"Failed to write rating: {str(e)}")

    prev = None
    if "Attributes" in resp and resp["Attributes"] and "value" in resp["Attributes"]:
        try:
            prev = int(resp["Attributes"]["value"])
        except Exception:
            prev = None

    status = "created" if prev is None else ("unchanged" if prev == val else "updated")
    return _json({
        "song_id": sid,
        "user_id": uid,
        "value": val,
        "status": status
    })
