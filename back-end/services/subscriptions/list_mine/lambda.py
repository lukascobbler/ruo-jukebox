import os, json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from pre_authorize import pre_authorize

dynamodb = boto3.resource("dynamodb")
ddb = boto3.client("dynamodb")
s3  = boto3.client("s3")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE,PATCH"
}

subs_table        = dynamodb.Table(os.environ["SUBSCRIPTIONS_TABLE"])
artists_table     = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genres_table_name = os.environ["GENRES_TABLE"]
images_bucket     = os.environ["IMAGES_BUCKET"]

def _presigned(key: str|None) -> str|None:
    if not key: return None
    try:
        return s3.generate_presigned_url("get_object",
               Params={"Bucket": images_bucket, "Key": key}, ExpiresIn=3600)
    except ClientError:
        return None

def _batch_get_artists(ids: list[str]) -> dict[str, dict]:
    out = {}
    if not ids: return out
    # simple batch in chunks of 100
    for i in range(0, len(ids), 100):
        keys = [{"artist_id": a} for a in ids[i:i+100]]
        resp = artists_table.batch_get_item(RequestItems={artists_table.name: {"Keys": keys}})
    out = {}
    for i in range(0, len(ids), 100):
        keys = [{"artist_id":{"S":a}} for a in ids[i:i+100]]
        r = ddb.batch_get_item(RequestItems={os.environ["ARTISTS_TABLE"]: {"Keys": keys}})
        for it in r["Responses"].get(os.environ["ARTISTS_TABLE"], []):
            item = {k: list(v.values())[0] for k,v in it.items()}
            out[item["artist_id"]] = item
    return out

def _batch_genre_names(ids: list[str]) -> dict[str, str]:
    if not ids: return {}
    out = {}
    for i in range(0, len(ids), 100):
        keys = [{"PK":{"S":"genres"}, "genre_id":{"S": gid}} for gid in ids[i:i+100]]
        resp = ddb.batch_get_item(RequestItems={genres_table_name: {"Keys": keys}})
        items = [{k: list(v.values())[0] for k, v in it.items()} for it in resp["Responses"].get(genres_table_name, [])]
        out.update({it["genre_id"]: it.get("Name","") for it in items})
    return out

@pre_authorize(['Admin','LoggedInUser'])
def lambda_handler(event, context):
    user_id = event.get("userId")
    if not user_id:
        return {"statusCode": 401, "headers": CORS_HEADERS, "body": json.dumps({"message":"Unauthorized"})}

    # query GSI by user
    topics, lek = [], None
    while True:
        kwargs = {"IndexName": "byUser", "KeyConditionExpression": Key("user_id").eq(user_id)}
        if lek: kwargs["ExclusiveStartKey"] = lek
        r = subs_table.query(**kwargs)
        topics.extend([it["topic"] for it in r.get("Items", [])])
        lek = r.get("LastEvaluatedKey")
        if not lek: break

    artist_ids = [t for t in topics if t.startswith("ARTIST~")]
    genre_ids  = [t for t in topics if t.startswith("GENRE~")]

    # fetch details
    artists_map = _batch_get_artists(artist_ids)
    genres_map  = _batch_genre_names(genre_ids)

    artists_out = []
    for aid in artist_ids:
        it = artists_map.get(aid)
        if not it: continue
        artists_out.append({
            "id": aid,
            "name": it.get("Name",""),
            "pictureKey": it.get("Picture"),
            "pictureUrl": _presigned(it.get("Picture")),
        })

    genres_out = [{"id": gid, "name": genres_map.get(gid,"")} for gid in genre_ids]

    return {"statusCode": 200, "headers": CORS_HEADERS,
            "body": json.dumps({"artists": artists_out, "genres": genres_out})}
