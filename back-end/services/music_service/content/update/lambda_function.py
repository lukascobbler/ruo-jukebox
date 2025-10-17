import os, json, boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
TRACKS = dynamodb.Table(os.environ["TRACKS_TABLE"])
TA     = dynamodb.Table(os.environ["TRACK_ARTISTS_TABLE"])
TG     = dynamodb.Table(os.environ["TRACK_GENRES_TABLE"])
def _claims(event):
    return (event.get("requestContext") or {}).get("authorizer", {}).get("claims", {}) or {}

def _require_admin(event):
    claims = _claims(event)
    groups = (claims.get("cognito:groups") or "")
    if "admin" not in groups.split(","):
        return {
            "statusCode": 403,
            "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps({"message":"admin only"})
        }

def _json_default(o):
    if isinstance(o, Decimal):
        return int(o) if o % 1 == 0 else float(o)
    raise TypeError

def _resp(code, body):
    return {"statusCode": code,
            "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body, default=_json_default)}

def lambda_handler(event, context):
    guard = _require_admin(event)
    if guard: 
        return guard
    track_id = event["pathParameters"]["id"]
    body = json.loads(event.get("body") or "{}")

    title     = body.get("title")
    album_id  = body.get("album_id", "__not_provided__")
    cover_key = body.get("cover_key", "__not_provided__")
    artist_ids = body.get("artist_ids")  # replace if provided
    genres     = body.get("genres")      # replace if provided

    # Build dynamic update for Track item
    sets, removes, eav = [], [], {}
    if title is not None:
        sets.append("title=:t"); eav[":t"]=title
    if album_id != "__not_provided__":
        if album_id is None:
            removes.append("album_id")
        else:
            sets.append("album_id=:al"); eav[":al"]=album_id
    if cover_key != "__not_provided__":
        if cover_key is None:
            removes.append("cover_key")
        else:
            sets.append("cover_key=:ck"); eav[":ck"]=cover_key

    if sets or removes:
        ue = []
        if sets: ue.append("SET " + ", ".join(sets))
        if removes: ue.append("REMOVE " + ", ".join(removes))
        TRACKS.update_item(
            Key={"track_id": track_id},
            UpdateExpression=" ".join(ue),
            ExpressionAttributeValues=(eav or None),
            ConditionExpression="attribute_exists(track_id)"
        )

    # Replace artists if provided
    if artist_ids is not None:
        # delete all current TA rows for track
        cur = TA.query(KeyConditionExpression=Key("track_id").eq(track_id))
        with TA.batch_writer() as bw:
            for it in cur.get("Items", []):
                bw.delete_item(Key={"track_id": track_id, "artist_id": it["artist_id"]})
            for aid in artist_ids:
                bw.put_item(Item={"track_id": track_id, "artist_id": aid})

    # Replace genres if provided
    if genres is not None:
        cur = TG.query(IndexName="byTrack", KeyConditionExpression=Key("track_id").eq(track_id))
        with TG.batch_writer() as bw:
            for it in cur.get("Items", []):
                bw.delete_item(Key={"genre": it["genre"], "track_id": track_id})
            for g in genres:
                bw.put_item(Item={"genre": g, "track_id": track_id})

    # Return updated track
    r = TRACKS.get_item(Key={"track_id": track_id})
    return _resp(200, r.get("Item") or {"track_id": track_id})
