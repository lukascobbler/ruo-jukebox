from datetime import datetime, timezone
import json, os, uuid, boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

SONGS_TABLE = os.environ["SONGS_TABLE"]
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    song_id = str(uuid.uuid4())
    filename = body.get("filename")
    cover_filename = body.get("cover_filename")

    if not filename:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Missing filename"})}

    audio_url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": AUDIO_BUCKET, "Key": f"songs/{song_id}/{filename}"},
        ExpiresIn=3600
    )

    response = {
        "song_id": song_id,
        "upload_url": audio_url
    }

    if cover_filename:
        cover_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": IMAGES_BUCKET, "Key": f"songs/{song_id}/cover/{cover_filename}"},
            ExpiresIn=3600
        )
        response["cover_upload_url"] = cover_url

    dynamodb.Table(SONGS_TABLE).put_item(
        Item={
            "song_id": song_id,
            "name": body.get("name"),
            "artist_ids": body.get("artist_ids", []),
            "genre_ids": body.get("genre_ids", []),
            "status": "UPLOADING",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    )

    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(response)}
