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
    body = json.loads(event.get("body") or "{}")
    q = event.get("queryStringParameters") or {}
    migrate = (q.get("migrate") in ["1","true","True","yes"])

    # fetch current
    gr = GENRES.get_item(Key={"genre_id": genre_id})
    item = gr.get("Item")
    if not item:
        return _resp(404, {"message":"Not found"})

    new_name = body.get("name")
    description = body.get("description")

    # update Genres table
    sets, eav = [], {}
    if new_name is not None:
        sets.append("name=:n"); eav[":n"]=new_name
    if description is not None:
        sets.append("description=:d"); eav[":d"]=description

    if sets:
        GENRES.update_item(
            Key={"genre_id": genre_id},
            UpdateExpression="SET " + ", ".join(sets),
            ExpressionAttributeValues=eav
        )

    # optional migration: rename join rows from old name -> new name
    if new_name and migrate and new_name != item.get("name"):
        old = item["name"]
        # query all TG rows under old name (PK)
        r = TG.query(KeyConditionExpression=Key("genre").eq(old))
        with TG.batch_writer() as bw:
            for it in r.get("Items", []):
                # create new row with new name
                bw.put_item(Item={"genre": new_name, "track_id": it["track_id"]})
                # delete old row
                bw.delete_item(Key={"genre": old, "track_id": it["track_id"]})

    # return updated doc
    r2 = GENRES.get_item(Key={"genre_id": genre_id})
    return _resp(200, r2.get("Item"))
