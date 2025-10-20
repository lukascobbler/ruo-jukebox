from datetime import datetime, timezone
import json, boto3, os

dynamodb = boto3.resource("dynamodb")
SONGS_TABLE = dynamodb.Table(os.environ["SONGS_TABLE"])

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        song_id = body.get("song_id")

        if not song_id:
            return _response(400, {"message": "Missing song_id"})

        SONGS_TABLE.update_item(
            Key={"song_id": song_id},
            UpdateExpression="SET #s = :s, uploaded_at = :t",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s": "UPLOADED",
                ":t": int(datetime.now(timezone.utc).timestamp())
            }
        )

        return _response(200, {"message": "Upload complete"})

    except Exception as e:
        return _response(500, {"message": str(e)})


def _response(status, body):
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body, default=str)}
