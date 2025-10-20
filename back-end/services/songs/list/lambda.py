from boto3.dynamodb.conditions import Key
import boto3, os, json

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client('s3', os.environ["REGION"], endpoint_url=os.environ["S3_ENDPOINT_URL"])

AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
SONGS_TABLE = dynamodb.Table(os.environ["SONGS_TABLE"])
SONG_ARTISTS_TABLE = dynamodb.Table(os.environ["SONG_ARTISTS_TABLE"])
CONTENT_GENRES_TABLE = dynamodb.Table(os.environ["CONTENT_GENRES_TABLE"])
CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))


def _generate_download_url(bucket, key):
    if not key: return None
    return s3.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=3600)


# TODO put actual names of genres and artists instead of IDs
def _get_artists(song_id):
    res = SONG_ARTISTS_TABLE.query(KeyConditionExpression=Key("song_id").eq(song_id))
    print(res)
    print(res.get("Items", []))
    return [{"name": item["artist_id"]} for item in res.get("Items", [])]


def _get_genres(song_id):
    res = CONTENT_GENRES_TABLE.query(IndexName="byEntity", KeyConditionExpression=Key("entity").eq(song_id))
    print(res)
    print(res.get("Items", []))
    return [{"name": item["genre"]} for item in res.get("Items", [])]


def lambda_handler(event, context):
    try:
        # Query only singles (album_id = "SINGLE")
        data = SONGS_TABLE.query(
            IndexName="byAlbum",
            KeyConditionExpression=Key("album_id").eq("SINGLE")
        )

        items = data.get("Items", [])

        for song in items:
            song_id = song.get("song_id")
            audio_key = song.get("audio_key")
            cover_key = song.get("cover_key")
            song["audio_url"] = _generate_download_url(AUDIO_BUCKET, audio_key)
            song["cover_url"] = _generate_download_url(IMAGES_BUCKET, cover_key)
            song["artists"] = _get_artists(song_id)
            song["genres"] = _get_genres(song_id)

        return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(items, default=str)}

    except Exception as e:
        return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"message": str(e)})}
