import json
import os
import boto3
from botocore.exceptions import ClientError

import decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o) if o % 1 == 0 else float(o)
        return super(DecimalEncoder, self).default(o)


# Environment
ALBUMS_TABLE = os.environ.get("ALBUMS_TABLE")
CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))

dynamodb = boto3.resource("dynamodb")
albums_table = dynamodb.Table(ALBUMS_TABLE)


def lambda_handler(event, context):
    try:
        response = albums_table.scan()  # todo
        items = response.get("Items", [])

        albums = []
        for item in items:
            albums.append({
                "id": item.get("album_id"),
                "name": item.get("name"),
                "released": bool(item.get("released")),
                "artistId": item.get("primary_artist_id"),
                "genres": item.get("genre_ids", []),
                "createdAt": item.get("created_at")
            })

        albums.sort(key=lambda x: x.get("createdAt", 0), reverse=True)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(albums, cls=DecimalEncoder)
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
