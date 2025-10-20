from boto3.dynamodb.conditions import Key
import json, os, boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

SONGS_TABLE = dynamodb.Table(os.environ["SONGS_TABLE"])
SONG_ARTISTS_TABLE = dynamodb.Table(os.environ["SONG_ARTISTS_TABLE"])
CONTENT_GENRES_TABLE = dynamodb.Table(os.environ["CONTENT_GENRES_TABLE"])
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
TRANSCRIPTS_BUCKET = os.environ.get("TRANSCRIPTS_BUCKET", "")

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

        # 1. Delete related records from SONG_ARTISTS_TABLE
        _delete_song_artists(song_id)

        # 2. Delete related records from CONTENT_GENRES_TABLE
        _delete_content_genres(song_id)

        # 3. Delete from DynamoDB main SONGS_TABLE
        SONGS_TABLE.delete_item(Key={"song_id": song_id})

        # 4. Delete S3 files if keys exist
        for bucket, key in [
            (AUDIO_BUCKET, item.get("audio_key")),
            (IMAGES_BUCKET, item.get("cover_key")),
            (TRANSCRIPTS_BUCKET, item.get("transcription_key")),
        ]:
            if key:
                _safe_delete_s3(bucket, key)

        # TODO cascade delete

        return _response(200, {"message": "Song and related data deleted successfully"})

    except Exception as e:
        return _response(500, {"error": str(e)})


def _delete_song_artists(song_id):
    res = SONG_ARTISTS_TABLE.query(KeyConditionExpression=Key("song_id").eq(song_id))
    items = res.get("Items", [])
    if not items: return
    with SONG_ARTISTS_TABLE.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={"song_id": song_id, "artist_id": item["artist_id"]})


def _delete_content_genres(song_id):
    res = CONTENT_GENRES_TABLE.query(IndexName="byEntity", KeyConditionExpression=Key("entity").eq(song_id))
    items = res.get("Items", [])
    if not items: return
    with CONTENT_GENRES_TABLE.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={"genre": item["genre"], "entity": song_id})


def _safe_delete_s3(bucket, key):
    if not bucket or not key: return
    try:
        s3.delete_object(Bucket=bucket, Key=key)
    except Exception:
        pass


def _response(status, body):
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body, default=str)}
