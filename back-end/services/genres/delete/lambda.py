import os, json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from services.common import _response

dynamodb = boto3.resource("dynamodb")
GENRES_TABLE = os.environ["GENRES_TABLE"]
CONTENT_GENRES_TABLE = os.environ["CONTENT_GENRES_TABLE"]

genres_table = dynamodb.Table(GENRES_TABLE)
content_genres_table = dynamodb.Table(CONTENT_GENRES_TABLE)


def lambda_handler(event, context):
    path = event.get("pathParameters") or {}
    genre_id = path.get("id")
    if not genre_id:
        return _response(400, {"message": "Genre id missing"})

    got = genres_table.get_item(Key={"PK": "genres", "genre_id": genre_id}).get("Item")
    if not got:
        return _response(404, {"message": "Genre not found"})

    deleted_links = _delete_all_content_genres(genre_id)

    try:
        genres_table.delete_item(
            Key={"PK": "genres", "genre_id": genre_id},
            ConditionExpression="attribute_exists(PK) AND attribute_exists(genre_id)"
        )
        deleted_genre = 1
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            # Someone else deleted the genre in the meantime
            deleted_genre = 0
        else:
            return _response(500, {"message": "Failed to delete genre", "error": str(e)})

    return _response(200, {
        "id": genre_id,
        "deleted": {
            "content_genres": deleted_links,
            "genre": deleted_genre
        }
    })

# maybe add async version

def _delete_all_content_genres(genre_id: str) -> int:
    total = 0
    last_key = None
    while True:
        kwargs = {
            "KeyConditionExpression": Key("genre").eq(genre_id),
            "ProjectionExpression": "#g",
            "ExpressionAttributeNames": {"#g": "genre"},
        }
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key

        resp = content_genres_table.query(**kwargs)
        items = resp.get("Items", [])
        if not items:
            break

        with content_genres_table.batch_writer() as batch:
            for it in items:
                batch.delete_item(Key={"genre": it["genre"]})
                total += 1

        last_key = resp.get("LastEvaluatedKey")
        if not last_key:
            break

    return total