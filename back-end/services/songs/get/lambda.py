from boto3.dynamodb.conditions import Key
import boto3, os, json

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


def _generate_download_url(bucket, key):
    if not key: return None
    return s3.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=3600)


def _get_related_ids(table, song_id, attr_name):
    res = table.query(KeyConditionExpression=Key("song_id").eq(song_id))
    return [item[attr_name] for item in res.get("Items", [])]


def lambda_handler(event, context):
    try:
        song_id = event.get("pathParameters", {}).get("id")
        if not song_id:
            return _response(400, {"error": "Missing song ID in path"})

        res = SONGS_TABLE.get_item(Key={"song_id": song_id})
        if "Item" not in res:
            return _response(404, {"error": "Song not found"})

        song = res["Item"]

        audio_key = song.get("audio_key")
        cover_key = song.get("cover_key")

        song["audio_url"] = _generate_download_url(AUDIO_BUCKET, audio_key) if audio_key else None
        song["cover_url"] = _generate_download_url(IMAGES_BUCKET, cover_key) if cover_key else None

        song["artist_ids"] = _get_related_ids(SONG_ARTISTS_TABLE, song_id, "artist_id")
        song["genre_ids"] = _get_related_ids(CONTENT_GENRES_TABLE, song_id, "genre_id")

        return _response(200, song)

    except Exception as e:
        return _response(500, {"error": str(e)})


def _response(status, body):
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body, default=str)}
