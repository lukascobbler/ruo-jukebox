import os, json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from pre_authorize import pre_authorize

dynamodb = boto3.resource("dynamodb")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,GET",
    "Content-Type": "application/json",
}

artists_table        = dynamodb.Table(os.environ["ARTISTS_TABLE"])
content_genres_table = dynamodb.Table(os.environ["CONTENT_GENRES_TABLE"])
genres_table         = dynamodb.Table(os.environ["GENRES_TABLE"])

def _scan_all_artists() -> list[dict]:
    items, lek = [], None
    while True:
        kwargs = {
            # Only read what we need; we won’t return picture anyway
            "ProjectionExpression": "artist_id, #n, Biography",
            "ExpressionAttributeNames": {"#n": "Name"},
        }
        if lek:
            kwargs["ExclusiveStartKey"] = lek
        resp = artists_table.scan(**kwargs)
        items.extend(resp.get("Items", []))
        lek = resp.get("LastEvaluatedKey")
        if not lek:
            break
    # deterministic order (by name)
    items.sort(key=lambda it: (it.get("Name") or "").lower())
    return items

def _all_genre_names() -> dict[str, str]:
    items, lek = [], None
    while True:
        kwargs = {
            "KeyConditionExpression": Key("PK").eq("genres"),
            "ProjectionExpression": "#pk, genre_id, #n",
            "ExpressionAttributeNames": {"#pk": "PK", "#n": "Name"},
        }
        if lek:
            kwargs["ExclusiveStartKey"] = lek
        resp = genres_table.query(**kwargs)
        items.extend(resp.get("Items", []))
        lek = resp.get("LastEvaluatedKey")
        if not lek:
            break
    return {it["genre_id"]: it.get("Name", "") for it in items}

def _all_artist_genre_links() -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    lek = None
    while True:
        kwargs = {
            "FilterExpression": Attr("entity").begins_with("ARTIST~"),
            "ProjectionExpression": "#g, #e",
            "ExpressionAttributeNames": {"#g": "genre", "#e": "entity"},
        }
        if lek:
            kwargs["ExclusiveStartKey"] = lek
        resp = content_genres_table.scan(**kwargs)
        for it in resp.get("Items", []):
            mapping.setdefault(it["entity"], []).append(it["genre"])
        lek = resp.get("LastEvaluatedKey")
        if not lek:
            break
    return mapping

@pre_authorize(['Admin', 'LoggedInUser'])
def lambda_handler(event, context):
    artist_items = _scan_all_artists()
    gid_to_name = _all_genre_names()
    artist_to_genres = _all_artist_genre_links()

    out = []
    for it in artist_items:
        aid = it["artist_id"]
        out.append({
            "id": aid,
            "name": it.get("Name", ""),
            "biography": it.get("Biography", "") or "",
            "pictureKey": None,         
            "pictureUrl": None,        
            "genres": [
                {"id": gid, "name": gid_to_name.get(gid, "")}
                for gid in artist_to_genres.get(aid, [])
            ],
        })

    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(out)}
