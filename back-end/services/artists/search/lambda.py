from boto3.dynamodb.conditions import Key, Attr
from pre_authorize import pre_authorize
import os, json, boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client('s3', os.environ["REGION"], endpoint_url=os.environ["S3_ENDPOINT_URL"])

CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
content_genres_table = dynamodb.Table(os.environ["CONTENT_GENRES_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
images_bucket = os.environ["IMAGES_BUCKET"]  # for presign


def _genre_names_map() -> dict[str, str]:
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


def _genres_for_artist(artist_id: str) -> list[str]:
    out, lek = [], None
    while True:
        kwargs = {
            "IndexName": "byEntity",  # ContentGenres GSI (entity -> genre)
            "KeyConditionExpression": Key("entity").eq(artist_id),
            "ProjectionExpression": "genre",
        }
        if lek: kwargs["ExclusiveStartKey"] = lek
        resp = content_genres_table.query(**kwargs)
        out.extend([it["genre"] for it in resp.get("Items", [])])
        lek = resp.get("LastEvaluatedKey")
        if not lek: break
    return out


def _presign(key: str | None) -> str | None:
    if not key: return None
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": images_bucket, "Key": key},
        ExpiresIn=3600,
    )


@pre_authorize(['Admin', 'LoggedInUser'])
def lambda_handler(event, context):
    qs = event.get("queryStringParameters") or {}
    q_raw = (qs.get("q") or "").strip()
    if not q_raw:
        return {"statusCode": 400, "headers": CORS_HEADERS,
                "body": json.dumps({"message": "Query parameter 'q' is required"})}

    q = " ".join(q_raw.lower().split())  # normalize whitespace

    # 1) Exact match via GSI byName (name_lc == q) — optional if GSI exists
    exact_items = []
    try:
        exact_resp = artists_table.query(
            IndexName="byName",
            KeyConditionExpression=Key("name_lc").eq(q),
            ProjectionExpression="artist_id, #n, Biography, Picture, name_lc",
            ExpressionAttributeNames={"#n": "Name"},
        )
        exact_items = exact_resp.get("Items", [])
    except Exception:
        exact_items = []

    # 2) Prefix / contains via Scan — OK for small dataset
    scan_items, lek = [], None
    filter_expr = Attr("name_lc").begins_with(q) | Attr("name_lc").contains(q)
    while True:
        kwargs = {
            "ProjectionExpression": "artist_id, #n, Biography, Picture, name_lc",
            "ExpressionAttributeNames": {"#n": "Name"},
            "FilterExpression": filter_expr,
        }
        if lek: kwargs["ExclusiveStartKey"] = lek
        resp = artists_table.scan(**kwargs)
        scan_items.extend(resp.get("Items", []))
        lek = resp.get("LastEvaluatedKey")
        if not lek: break

    # 3) Rank: exact, then prefix, then contains; dedupe by artist_id
    seen, ranked = set(), []

    def push(items):
        for it in items:
            aid = it["artist_id"]
            if aid in seen: continue
            seen.add(aid);
            ranked.append(it)

    push(exact_items)
    prefix = [it for it in scan_items if (it.get("name_lc") or "").startswith(q)]
    contains = [it for it in scan_items if it not in prefix]
    prefix.sort(key=lambda it: (it.get("Name") or "").lower())
    contains.sort(key=lambda it: (it.get("Name") or "").lower())
    push(prefix);
    push(contains)

    # 4) Attach genres + presigned image (no limit; return all)
    gid_to_name = _genre_names_map()
    out = []
    for it in ranked:
        aid = it["artist_id"]
        picture_key = it.get("Picture")
        gids = _genres_for_artist(aid)
        out.append({
            "id": aid,
            "name": it.get("Name", ""),
            "biography": it.get("Biography", "") or "",
            "pictureKey": picture_key or None,
            "pictureUrl": _presign(picture_key) if picture_key else None,
            "genres": [{"id": gid, "name": gid_to_name.get(gid, "")} for gid in gids],
        })

    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(out)}
