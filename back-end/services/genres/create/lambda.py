import os, json, re, time, secrets
import boto3
from botocore.exceptions import ClientError
from services.common import _response

dynamodb = boto3.resource("dynamodb")
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])

# helpers for id generation TODO maybe move to common or change
_slug_re = re.compile(r"[^a-z0-9]+")
def _slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = _slug_re.sub("-", s).strip("-")
    return s or "genre" # "Alt Rock" -> "alt-rock"

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"message": "Invalid JSON body"})

    name = (body.get("name") or "").strip()
    if not name:
        return _response(400, {"message": "Field 'name' is required"})

    genre_id = _slugify(name)
    now = int(time.time())

    item = {
        "PK": "genres",
        "genre_id": genre_id,
        "Name": name,
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
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            # another genre already owns this slug => treat as duplicate (if there is Rock, we will discard rOck, rOCk etc)
            return _response(409, {"message": f"Genre '{name}' already exists"})
        return _response(500, {"message": "Failed to create genre", "error": str(e)})