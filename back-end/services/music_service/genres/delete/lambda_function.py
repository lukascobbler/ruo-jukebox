import os, json, boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
GENRES = dynamodb.Table(os.environ["GENRES_TABLE"])
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
    genre_id = event["pathParameters"]["id"]
    q = event.get("queryStringParameters") or {}
    force = (q.get("force") in ["1","true","True","yes"])

    gr = GENRES.get_item(Key={"genre_id": genre_id})
    g = gr.get("Item")
    if not g:
        return _resp(404, {"message":"Not found"})

    # TrackGenres uses the NAME as PK; find references by the current name
    name = g.get("name")
    refs = TG.query(KeyConditionExpression=Key("genre").eq(name))
    count = refs.get("Count", 0)

    if count and not force:
        return _resp(409, {"message":"genre in use; call with ?force=true to remove joins first", "count": count})

    # remove joins if any
    if count:
        with TG.batch_writer() as bw:
            for it in refs.get("Items", []):
                bw.delete_item(Key={"genre": name, "track_id": it["track_id"]})

    GENRES.delete_item(Key={"genre_id": genre_id})
    return _resp(204, "")
