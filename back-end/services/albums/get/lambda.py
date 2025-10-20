import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

ALBUMS_TABLE = os.environ.get("ALBUMS_TABLE")
SONGS_TABLE = os.environ.get("SONGS_TABLE")
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PATCH,DELETE"
}

dynamodb = boto3.resource("dynamodb")
albums_table = dynamodb.Table(ALBUMS_TABLE)
songs_table = dynamodb.Table(SONGS_TABLE)


def lambda_handler(event, context):
    try:
        album_id = event.get("pathParameters", {}).get("id")
        if not album_id:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"message": "Missing album ID"})
            }

        album_resp = albums_table.get_item(Key={"album_id": album_id})
        album = album_resp.get("Item")

        if not album:
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({"message": "Album not found"})
            }

        songs_resp = songs_table.query(
            IndexName="byAlbum",
            KeyConditionExpression=Key("album_id").eq(album_id),
            ScanIndexForward=True
        )

        songs_items = songs_resp.get("Items", [])

        songs = [
            {
                "id": s.get("song_id"),
                "title": s.get("title"),
                "songNo": s.get("song_no"),
                "duration": s.get("duration"),
            }
            for s in songs_items
        ]

        album_data = {
            "id": album.get("album_id"),
            "name": album.get("name"),
            "released": bool(album.get("released", False)),
            "artistId": album.get("primary_artist_id"),
            "artist": album.get("artist_name", "Unknown Artist"),
            "genres": album.get("genre_ids", []),
            "songs": songs
        }

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(album_data)
        }

    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "UnknownError")
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": f"DynamoDB error ({code}): {str(e)}"
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": f"Internal server error: {str(e)}"
            })
        }
