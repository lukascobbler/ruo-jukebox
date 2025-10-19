import os, json, time, uuid
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
ddb = boto3.client("dynamodb")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
}

artists = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genres_table_name = os.environ["GENRES_TABLE"]
content_genres = dynamodb.Table(os.environ["CONTENT_GENRES_TABLE"])

def _parse_genre_ids(x):
    if x is None: return []
    if isinstance(x, str): x = [x]
    if not isinstance(x, list): return []
    out = []
    for g in x:
        if isinstance(g, str):
            g = g.strip()
            if g: out.append(g)
    # dedupe, keep order
    seen, uniq = set(), []
    for g in out:
        if g not in seen:
            seen.add(g); uniq.append(g)
    return uniq

def _batch_genre_names(ids):
    if not ids: return {}
    out = {}
    for i in range(0, len(ids), 100):
        keys = [{"PK":{"S":"genres"}, "genre_id":{"S": gid}} for gid in ids[i:i+100]]
        resp = ddb.batch_get_item(RequestItems={genres_table_name: {"Keys": keys}})
        items = [{k: list(v.values())[0] for k, v in it.items()} for it in resp["Responses"].get(genres_table_name, [])]
        out.update({it["genre_id"]: it.get("Name","") for it in items})
    return out

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Invalid JSON body"})}

    name = (body.get("name") or "").strip()
    biography = (body.get("biography") or "").strip()
    genres = _parse_genre_ids(body.get("genres"))
    picture_key = (body.get("pictureKey") or "").strip()

    if not name: return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Field 'name' is required"})}
    if not biography: return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Field 'biography' is required"})}
    if not genres: return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Field 'genres' must contain at least one genre id"})}

    # validate genres
    names = _batch_genre_names(genres)
    missing = [g for g in genres if g not in names]
    if missing:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Unknown genre ids", "unknown": missing})}

    now = int(time.time())
    artist_id = f"ARTIST~{uuid.uuid4().hex}"

    item = {
        "artist_id": artist_id,
        "Name": name,
        "name_lc": name.lower(),
        "Biography": biography,
        "created_at": now,
        "updated_at": now,
    }
    if picture_key:
        item["Picture"] = picture_key

    try:
        artists.put_item(Item=item, ConditionExpression="attribute_not_exists(artist_id)")
    except ClientError as e:
        return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"message": "Failed to create artist", "error": str(e)})}

    with content_genres.batch_writer() as batch:
        for gid in genres:
            batch.put_item(Item={"genre": gid, "entity": artist_id})

    return {"statusCode": 201, "headers": CORS_HEADERS, "body": json.dumps({"id": artist_id,"name": name,"biography": biography,"pictureKey": item.get("Picture"),"genres": [{"id": gid, "name": names.get(gid, "")} for gid in genres]})}
