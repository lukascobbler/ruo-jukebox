import os, json, time, uuid
import boto3
from botocore.exceptions import ClientError
from services.common import _response

dynamodb = boto3.resource("dynamodb")
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"message": "Invalid JSON body"})

    name = (body.get("name") or "").strip()
    if not name:
        return _response(400, {"message": "Field 'name' is required"})

    genre_id = f"GENRE~{uuid.uuid4().hex}"
    now = int(time.time())

    item = {
        "PK": "genres",
        "genre_id": genre_id,
        "Name": name,
        "name_lc": name.lower(),
        "created_at": now,
        "updated_at": now,
    }

    try:
        genres_table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(genre_id)"
        )
        return _response(201, {"id": genre_id, "name": name})
    except ClientError as e:
        return _response(500, {"message": "Failed to create genre", "error": str(e)})
