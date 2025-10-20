import json, os, boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

SONGS_TABLE = dynamodb.Table(os.environ["SONGS_TABLE"])
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
TRANSCRIPTS_BUCKET = os.environ["TRANSCRIPTS_BUCKET"]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}


def lambda_handler(event, context):
    try:
        song_id = event.get("pathParameters", {}).get("id")
        if not song_id:
            return _response(400, {"error": "Missing song ID"})

        res = SONGS_TABLE.get_item(Key={"song_id": song_id})
        item = res.get("Item")

        if not item:
            return _response(404, {"error": "Song not found"})

        # 1. Delete from DynamoDB
        SONGS_TABLE.delete_item(Key={"song_id": song_id})

        # 2. Delete individual files by stored keys
        if item.get("audio_key"):
            _safe_delete_s3(AUDIO_BUCKET, item["audio_key"])

        if item.get("cover_key"):
            _safe_delete_s3(IMAGES_BUCKET, item["cover_key"])

        if item.get("transcription_key"):
            _safe_delete_s3(TRANSCRIPTS_BUCKET, item["transcription_key"])

        # TODO cascade delete

        return _response(200, {"message": "Song deleted successfully"})

    except Exception as e:
        return _response(500, {"error": str(e)})


def _safe_delete_s3(bucket, key):
    try:
        s3.delete_object(Bucket=bucket, Key=key)
    except Exception:
        pass


def _response(status, body):
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body, default=str)}
