import os, json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from pre_authorize import pre_authorize

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,GET",
    "Content-Type": "application/json",
}

artists_table        = dynamodb.Table(os.environ["ARTISTS_TABLE"])
content_genres_table = dynamodb.Table(os.environ["CONTENT_GENRES_TABLE"])
genres_table         = dynamodb.Table(os.environ["GENRES_TABLE"])
images_bucket        = os.environ["IMAGES_BUCKET"]

def _ensure_genre_exists(genre_id: str) -> bool:
    resp = genres_table.get_item(Key={"PK": "genres", "genre_id": genre_id})
    return bool(resp.get("Item"))

def _artist_ids_for_genre(genre_id: str) -> list[str]:
    """
    Query ContentGenres partition 'genre' to get linked entities,
    keep only ARTIST~... entities.
    """
    ids = []
    lek = None
    while True:
        kwargs = {
            "KeyConditionExpression": Key("genre").eq(genre_id),
            "ProjectionExpression": "entity",
        }
        if lek: kwargs["ExclusiveStartKey"] = lek
        resp = content_genres_table.query(**kwargs)
        for it in resp.get("Items", []):
            ent = it.get("entity", "")
            if ent.startswith("ARTIST~"):
                ids.append(ent)
        lek = resp.get("LastEvaluatedKey")
        if not lek: break
    # dedupe, preserve order
    seen = set()
    uniq = []
    for a in ids:
        if a not in seen:
            seen.add(a); uniq.append(a)
    return uniq

def _batch_get_artists(artist_ids: list[str]) -> dict[str, dict]:
    if not artist_ids: return {}
    # batch_get_item in chunks of <=100
    ddb = boto3.client("dynamodb")
    out = {}
    for i in range(0, len(artist_ids), 100):
        keys = [{"artist_id": {"S": aid}} for aid in artist_ids[i:i+100]]
        resp = ddb.batch_get_item(
            RequestItems={ artists_table.name: {"Keys": keys} }
        )
        items = [
            {k: list(v.values())[0] for k, v in it.items()}
            for it in resp["Responses"].get(artists_table.name, [])
        ]
        for it in items:
            out[it["artist_id"]] = it
    return out

def _genre_names_map() -> dict[str, str]:
    """Query all genres once to map id -> Name."""
    items, lek = [], None
    while True:
        kwargs = {
            "KeyConditionExpression": Key("PK").eq("genres"),
            "ProjectionExpression": "#pk, genre_id, #n",
            "ExpressionAttributeNames": {"#pk": "PK", "#n": "Name"},
        }
        if lek: kwargs["ExclusiveStartKey"] = lek
        resp = genres_table.query(**kwargs)
        items.extend(resp.get("Items", []))
        lek = resp.get("LastEvaluatedKey")
        if not lek: break
    return {it["genre_id"]: it.get("Name", "") for it in items}

def _all_genres_for_artists(artist_ids: list[str]) -> dict[str, list[str]]:
    """
    For each artist, query GSI 'byEntity' to get all genre_ids.
    Since dataset is small, per-artist queries are acceptable.
    """
    mapping: dict[str, list[str]] = {aid: [] for aid in artist_ids}
    for aid in artist_ids:
        lek = None
        while True:
            kwargs = {
                "IndexName": "byEntity",
                "KeyConditionExpression": Key("entity").eq(aid),
                "ProjectionExpression": "genre",
            }
            if lek: kwargs["ExclusiveStartKey"] = lek
            resp = content_genres_table.query(**kwargs)
            mapping[aid].extend([it["genre"] for it in resp.get("Items", [])])
            lek = resp.get("LastEvaluatedKey")
            if not lek: break
    return mapping

def _presign(key: str | None) -> str | None:
    if not key: return None
    try:
        return s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": images_bucket, "Key": key},
            ExpiresIn=3600
        )
    except ClientError:
        return None

@pre_authorize(['Admin', 'LoggedInUser'])
def lambda_handler(event, context):
    genre_id = (event.get("pathParameters") or {}).get("id") or ""
    genre_id = genre_id.strip()
    if not genre_id or not genre_id.startswith("GENRE~"):
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Invalid or missing genre id"})}

    # Optional: validate the genre exists
    if not _ensure_genre_exists(genre_id):
        return {"statusCode": 404, "headers": CORS_HEADERS, "body": json.dumps({"message": "Genre not found"})}

    artist_ids = _artist_ids_for_genre(genre_id)
    if not artist_ids:
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps([])}

    artists = _batch_get_artists(artist_ids)
    gid_to_name = _genre_names_map()
    artist_to_gids = _all_genres_for_artists(artist_ids)

    out = []
    for aid in artist_ids:  # keep stable order
        it = artists.get(aid) or {}
        name = it.get("Name", "")
        bio  = it.get("Biography", "") or ""
        picture_key = it.get("Picture")

        out.append({
            "id": aid,
            "name": name,
            "biography": bio,
            "pictureKey": picture_key or None,
            "pictureUrl": _presign(picture_key) if picture_key else None,
            "genres": [
                {"id": gid, "name": gid_to_name.get(gid, "")}
                for gid in artist_to_gids.get(aid, [])
            ],
        })

    # sort by name, case-insensitive
    out.sort(key=lambda a: (a.get("name") or "").lower())

    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(out)}
