import os, json, time, uuid
import boto3
from botocore.exceptions import ClientError
from services.common import _response

dynamodb = boto3.resource("dynamodb")
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
# fali content genres table, to cemo kad popravimo kako radi sort key

def _as_genre_ids(x):
    if x is None:
        return []
    if isinstance(x, list):
        # minimal sanitation: strings only, strip, dedupe, keep order
        seen, out = set(), []
        for g in x:
            if not isinstance(g, str):
                continue
            g = g.strip()
            if not g or g in seen:
                continue
            seen.add(g)
            out.append(g)
        return out
    # single string -> list
    if isinstance(x, str):
        s = x.strip()
        return [s] if s else []
    return []

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"message": "Invalid JSON body"})

    name = (body.get("name") or "").strip()
    bio  = (body.get("biography") or "").strip()
    if not name:
        return _response(400, {"message": "Field 'name' is required"})
    if not bio:
        return _response(400, {"message": "Field 'bio' is required"})

    genres = _as_genre_ids(body.get("genres"))

    now = int(time.time())
    artist_id = uuid.uuid4().hex # proveriti da li cemo semu

    item = {
        "artist_id": artist_id,
        "Name": name,
        "name_lc": name.lower(),
        "Biography": bio,
        "created_at": now,
        "updated_at": now,
    }

    try:
        artists_table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(artist_id)"
        )
    except ClientError as e:
        return _response(500, {"message": "Failed to create artist", "error": str(e)})

    # TODO srediti genres u content-genres tabeli
    return _response(201, {
        "id": artist_id,
        "name": name,
        "biography": bio,
        "genres": genres
    })
