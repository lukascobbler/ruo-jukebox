from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from pre_authorize import pre_authorize
import boto3, json, os

ALBUMS_TABLE = os.environ.get("ALBUMS_TABLE")
SONGS_TABLE = os.environ.get("SONGS_TABLE")
CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))

dynamodb = boto3.resource("dynamodb")
albums_table = dynamodb.Table(ALBUMS_TABLE)
songs_table = dynamodb.Table(SONGS_TABLE)


def _response(status, body):
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body, default=str)}


@pre_authorize(['Admin', 'LoggedInUser'])
def lambda_handler(event, context):
    # try:
    print("alive1")
    album_id = event.get("pathParameters", {}).get("id")
    if not album_id:
        return _response(400, {"message": "Missing album ID"})

    album_resp = albums_table.get_item(Key={"album_id": album_id})
    album = album_resp.get("Item")
    print("alive2")

    if not album:
        return _response(404, {"message": "Album not found"})

    songs_resp = songs_table.query(
        IndexName="byAlbum",
        KeyConditionExpression=Key("album_id").eq(album_id),
        ScanIndexForward=True
    )
    print("alive3")

    songs_items = songs_resp.get("Items", [])

    songs = [{
        "id": s.get("song_id"),
        "title": s.get("title"),
        "songNo": s.get("song_no"),
        "duration": s.get("duration"),
    } for s in songs_items]

    print("alive4")
    album_data = {
        "id": album.get("album_id"),
        "name": album.get("name"),
        "released": bool(album.get("released", False)),
        "artistId": album.get("primary_artist_id"),
        "artist": album.get("artist_name", "Unknown Artist"),
        "genres": album.get("genre_ids", []),
        "songs": songs
    }
    print("alive5")

    return _response(200, album_data)
    #
    # except ClientError as e:
    #     code = e.response.get("Error", {}).get("Code", "UnknownError")
    #     return _response(500, {"message": f"DynamoDB error ({code}): {str(e)}"})

    # except Exception as e:
    #     return _response(500, {"message": f"Internal server error: {str(e)}"})
