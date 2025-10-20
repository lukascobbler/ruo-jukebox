import json
import os
import uuid
import time
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from pre_authorize import pre_authorize

ALBUMS_TABLE = os.environ.get("ALBUMS_TABLE")
ARTISTS_TABLE = os.environ.get("ARTISTS_TABLE")  # optional, for validation
GENRES_TABLE = os.environ.get("GENRES_TABLE")    # optional
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PATCH,DELETE"
}

dynamodb = boto3.resource("dynamodb")
ddb_client = boto3.client("dynamodb")

albums_table = dynamodb.Table(ALBUMS_TABLE)

@pre_authorize(['Admin'])
def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        name = body.get("name")
        artist_id = body.get("artistId")
        genre_ids = body.get("genreIds", [])

        if not name or not artist_id or not isinstance(genre_ids, list) or not genre_ids:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"message": "Missing or invalid fields"})
            }

        # todo validate that artist and genres exist

        album_id = str(uuid.uuid4())
        now = int(time.time())

        album_item = {
            "album_id": album_id,
            "name": name,
            "artist_id": artist_id,
            "genre_ids": genre_ids,
            "created_at": now,
            "released": False
        }

        albums_table.put_item(Item=album_item)

        return {
            "statusCode": 201,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "id": album_id,
                "name": name
            })
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
