from boto3.dynamodb.conditions import Key
import json, boto3, os

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client('s3', os.environ["REGION"], endpoint_url=os.environ["S3_ENDPOINT_URL"])

SONGS_TABLE = dynamodb.Table(os.environ["SONGS_TABLE"])
SONG_ARTISTS_TABLE = dynamodb.Table(os.environ["SONG_ARTISTS_TABLE"])
CONTENT_GENRES_TABLE = dynamodb.Table(os.environ["CONTENT_GENRES_TABLE"])
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}


def _generate_upload_url(bucket, key):
    return s3.generate_presigned_url("put_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=3600)


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


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        song_id = body.get("song_id")
        if not song_id:
            return _response(400, {"error": "Missing song_id"})

        update_expr = []
        expr_values = {}
        expr_names = {}
        response_data = {}

        if "name" in body:
            expr_names["#title"] = "title"
            update_expr.append("#title = :title")
            expr_values[":title"] = body["name"]

        if "cover_filename" in body:
            new_cover_key = f"singles/{song_id}.jpg"
            cover_url = _generate_upload_url(IMAGES_BUCKET, new_cover_key)
            update_expr.append("cover_key = :cover_key")
            expr_values[":cover_key"] = new_cover_key
            response_data["cover_upload_url"] = cover_url

        if "audio_filename" in body:
            new_audio_key = f"songs/{song_id}.mp3"
            audio_url = _generate_upload_url(AUDIO_BUCKET, new_audio_key)
            update_expr.append("audio_key = :audio_key")
            expr_values[":audio_key"] = new_audio_key
            response_data["audio_upload_url"] = audio_url

        if update_expr:
            update_statement = "SET " + ", ".join(update_expr)
            SONGS_TABLE.update_item(
                Key={"song_id": song_id},
                UpdateExpression=update_statement,
                ExpressionAttributeValues=expr_values,
                ExpressionAttributeNames=expr_names if expr_names else None
            )

        if "artist_ids" in body:
            _delete_song_artists(song_id)
            with SONG_ARTISTS_TABLE.batch_writer() as batch:
                for artist_id in body["artist_ids"]:
                    batch.put_item(Item={"song_id": song_id, "artist_id": artist_id})

        if "genre_ids" in body:
            _delete_content_genres(song_id)
            with CONTENT_GENRES_TABLE.batch_writer() as batch:
                for genre_id in body["genre_ids"]:
                    batch.put_item(Item={"genre": genre_id, "entity": song_id})

        response_data["message"] = "Song updated successfully"
        return _response(200, response_data)

    except Exception as e:
        return _response(500, {"error": str(e)})


def _response(status, body):
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body, default=str)}
