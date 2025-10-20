from datetime import datetime, timezone
import json, os, uuid, boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
SONGS_TABLE = dynamodb.Table(os.environ["SONGS_TABLE"])
SONG_ARTISTS_TABLE = dynamodb.Table(os.environ["SONG_ARTISTS_TABLE"])
CONTENT_GENRES_TABLE = dynamodb.Table(os.environ["CONTENT_GENRES_TABLE"])

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}


def _generate_presigned_url(bucket, key):
    return s3.generate_presigned_url("put_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=3600)


def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    name = body.get("name")
    filename = body.get("filename")
    cover_filename = body.get("cover_filename")

    if not name or not filename:
        return _response(400, {"message": "Missing filename"})

    song_id = str(uuid.uuid4())

    audio_key = f"songs/{song_id}.mp3"
    cover_key = f"singles/{song_id}.jpg" if cover_filename else None

    audio_url = _generate_presigned_url(AUDIO_BUCKET, audio_key)
    response = {"song_id": song_id, "upload_url": audio_url}

    if cover_key:
        response["cover_upload_url"] = _generate_presigned_url(IMAGES_BUCKET, cover_key)

    SONGS_TABLE.put_item(
        Item={
            "song_id": song_id,
            "title": name,
            "status": "UPLOADING",
            "audio_key": audio_key,
            "has_album": "false",
            "cover_key": cover_key or "",
            "created_at": int(datetime.now(timezone.utc).timestamp()),
            "stats": {"rating_sum": 0, "rating_cnt": 0},
        }
    )

    _store_song_artists(song_id, body.get("artists", []))
    _store_song_genres(song_id, body.get("genres", []))

    return _response(200, response)


def _store_song_artists(song_id, artists):
    if not artists: return
    with SONG_ARTISTS_TABLE.batch_writer() as batch:
        for artist_id in artists:
            batch.put_item(Item={"song_id": song_id, "artist_id": artist_id})


def _store_song_genres(song_id, genres):
    if not genres: return
    with CONTENT_GENRES_TABLE.batch_writer() as batch:
        for genre in genres:
            batch.put_item(Item={"entity": song_id, "genre": genre})


def _response(status, body):
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body, default=str)}
