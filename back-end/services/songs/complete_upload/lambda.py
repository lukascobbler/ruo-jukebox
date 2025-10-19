from datetime import datetime, timezone
import json, boto3, os

dynamodb = boto3.resource("dynamodb")
SONGS_TABLE = os.environ["SONGS_TABLE"]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    song_id = body.get("song_id")
    if not song_id:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Missing song_id"})}

    dynamodb.Table(SONGS_TABLE).update_item(
        Key={"song_id": song_id},
        UpdateExpression="SET #s = :s, uploaded_at = :t",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": "UPLOADED", ":t": datetime.now(timezone.utc).isoformat()}
    )

    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"message": "Upload complete"})}
