from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from pre_authorize import pre_authorize
import os, json, time, boto3

dynamodb = boto3.resource("dynamodb")
ddb = boto3.client("dynamodb")

CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))
artists = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genres_table_name = os.environ["GENRES_TABLE"]
content_genres = dynamodb.Table(os.environ["CONTENT_GENRES_TABLE"])

def _parse_genre_ids(x):
    if x is None: return None
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

def _current_genres(artist_id):
    out, lek = [], None
    while True:
        q = {"IndexName":"byEntity", "KeyConditionExpression": Key("entity").eq(artist_id)}
        if lek: q["ExclusiveStartKey"] = lek
        resp = content_genres.query(**q)
        out.extend([r["genre"] for r in resp.get("Items", [])])
        lek = resp.get("LastEvaluatedKey")
        if not lek: break
    return out

@pre_authorize(['Admin'])
def lambda_handler(event, context):
    artist_id = (event.get("pathParameters") or {}).get("id")
    if not artist_id:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Artist id missing in path"})}

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Invalid JSON body"})}

    has_name = "name" in body
    has_bio  = "biography" in body
    has_pic  = "pictureKey" in body
    has_gen  = "genres" in body
    if not (has_name or has_bio or has_pic or has_gen):
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Nothing to update"})}

    cur = artists.get_item(Key={"artist_id": artist_id}).get("Item")
    if not cur:
        return {"statusCode": 404, "headers": CORS_HEADERS, "body": json.dumps({"message": "Artist not found"})}

    names, values, sets = {"#u":"updated_at"}, {":now": int(time.time())}, ["#u=:now"]

    if has_name:
        nm = (body.get("name") or "").strip()
        if not nm: return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Field 'name' cannot be empty"})}
        names["#N"]="Name"; names["#nlc"]="name_lc"
        values[":n"]=nm; values[":nlc"]=nm.lower()
        sets += ["#N=:n", "#nlc=:nlc"]

    if has_bio:
        bio = (body.get("biography") or "").strip()
        names["#B"]="Biography"; values[":b"]=bio
        sets.append("#B=:b")

    if has_pic:
        pk = (body.get("pictureKey") or "").strip()
        if not pk: return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Field 'pictureKey' cannot be empty"})}
        names["#P"]="Picture"; values[":p"]=pk
        sets.append("#P=:p")

    try:
        artists.update_item(
            Key={"artist_id": artist_id},
            UpdateExpression="SET " + ", ".join(sets),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            ConditionExpression="attribute_exists(artist_id)"
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {"statusCode": 404, "headers": CORS_HEADERS, "body": json.dumps({"message":"Artist not found"})}
        return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"message":"Failed to update artist", "error": str(e)})}

    if has_gen:
        new_gen = _parse_genre_ids(body.get("genres")) or []
        # validate exist
        name_by = _batch_genre_names(new_gen)
        missing = [g for g in new_gen if g not in name_by]
        if missing:
            return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Unknown genre ids", "unknown": missing})}

        old = set(_current_genres(artist_id))
        new = set(new_gen)
        to_add, to_del = new - old, old - new

        if to_add or to_del:
            with content_genres.batch_writer() as batch:
                for gid in to_add:
                    batch.put_item(Item={"genre": gid, "entity": artist_id})
                for gid in to_del:
                    batch.delete_item(Key={"genre": gid, "entity": artist_id})

        genres_list = [{"id": gid, "name": name_by.get(gid,"")} for gid in new_gen]
    else:
        current = _current_genres(artist_id)
        name_by = _batch_genre_names(current)
        genres_list = [{"id": gid, "name": name_by.get(gid,"")} for gid in current]

    fresh = artists.get_item(Key={"artist_id": artist_id}).get("Item") or {}
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"id": artist_id,"name": fresh.get("Name",""),"biography": fresh.get("Biography",""),"pictureKey": fresh.get("Picture"),"genres": genres_list})}
