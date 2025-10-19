import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from pre_authorize import pre_authorize

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
}

artists_table        = dynamodb.Table(os.environ["ARTISTS_TABLE"])
content_genres_table = dynamodb.Table(os.environ["CONTENT_GENRES_TABLE"])
genres_table         = dynamodb.Table(os.environ["GENRES_TABLE"])
images_bucket        = os.environ["IMAGES_BUCKET"]

def _scan_all_artists() -> list[dict]:
    items, lek = [], None
    while True:
        kwargs = {}
        if lek:
            kwargs["ExclusiveStartKey"] = lek
        resp = artists_table.scan(**kwargs)
        items.extend(resp.get("Items", []))
        lek = resp.get("LastEvaluatedKey")
        if not lek:
            break
    return items

def _all_genre_names() -> dict[str, str]:
    """Query all genres once and return {genre_id: Name}."""
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
    """
    Scan ContentGenres once, keep only rows where entity starts with 'ARTIST~',
    and build {artist_id: [genre_id, ...]} mapping.
    """
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
            aid = it["entity"]
            gid = it["genre"]
            mapping.setdefault(aid, []).append(gid)
        lek = resp.get("LastEvaluatedKey")
        if not lek:
            break
    return mapping

def _presigned_picture_url(key: str | None) -> str | None:
    if not key:
        return None
    try:
        return s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": images_bucket, "Key": key},
            ExpiresIn=3600,  # 1h
        )
    except ClientError:
        return None

@pre_authorize(['Admin', 'LoggedInUser'])
def lambda_handler(event, context):
    artist_items = _scan_all_artists()

    gid_to_name = _all_genre_names()

    artist_to_genres = _all_artist_genre_links()

    out = []
    for it in artist_items:
        aid = it["artist_id"]
        picture_key = it.get("Picture")
        out.append({
            "id": aid,
            "name": it.get("Name", ""),
            "biography": it.get("Biography", "") or "",
            "pictureKey": picture_key,
            "pictureUrl": _presigned_picture_url(picture_key),
            "genres": [
                {"id": gid, "name": gid_to_name.get(gid, "")}
                for gid in artist_to_genres.get(aid, [])
            ],
        })

    return {"statusCode": 200, "headers": CORS_HEADERS, "body": out}
