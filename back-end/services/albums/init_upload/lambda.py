from datetime import datetime, timezone
import json, os, uuid, boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
ALBUMS_TABLE = dynamodb.Table(os.environ["ALBUMS_TABLE"])
ALBUM_ARTISTS_TABLE = dynamodb.Table(os.environ["ALBUM_ARTISTS_TABLE"])
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
    cover_filename = body.get("cover_filename")

    if not name:
        return _response(400, {"message": "Missing album name"})

    album_id = "ALBUM~" + str(uuid.uuid4())
    cover_key = f"albums/{album_id}.jpg" if cover_filename else None
    response = {"album_id": album_id}

    if cover_key:
        response["cover_upload_url"] = _generate_presigned_url(IMAGES_BUCKET, cover_key)

    ALBUMS_TABLE.put_item(
        Item={
            "album_id": album_id,
            "title": name,
            "status": "UPLOADING",
            "cover_key": cover_key or "",
            "created_at": int(datetime.now(timezone.utc).timestamp())
        }
    )

    _store_album_artists(album_id, body.get("artists", []))
    _store_album_genres(album_id, body.get("genres", []))

    return _response(200, response)


def _store_album_artists(album_id, artists):
    if not artists: return
    with ALBUM_ARTISTS_TABLE.batch_writer() as batch:
        for artist_id in artists:
            batch.put_item(Item={"album_id": album_id, "artist_id": artist_id})


def _store_album_genres(album_id, genres):
    if not genres: return
    with CONTENT_GENRES_TABLE.batch_writer() as batch:
        for genre in genres:
            batch.put_item(Item={"entity": album_id, "genre": genre})


def _response(status, body):
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body, default=str)}
