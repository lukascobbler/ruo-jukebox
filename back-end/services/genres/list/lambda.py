from boto3.dynamodb.conditions import Key
from pre_authorize import pre_authorize
from read import get_
import boto3, json, os

dynamodb = boto3.resource("dynamodb")
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
subs_table = dynamodb.Table(os.environ["SUBSCRIPTIONS_TABLE"])
CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))

@pre_authorize(["Admin", "User"])
def lambda_handler(event, context):
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

    if _is_admin(event):
        out = [{"id": it["genre_id"], "name": it.get("Name", ""), "isSubscribed": False} for it in items]
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(out)}

    uid = _user_id(event)
    user_topics = set()
    if uid:
        lek = None
        while True:
            q = {
                "IndexName": "byUser",
                "KeyConditionExpression": Key("user_id").eq(uid),
                "ProjectionExpression": "topic",
            }
            if lek:
                q["ExclusiveStartKey"] = lek
            r = subs_table.query(**q)
            for s in r.get("Items", []):
                t = s.get("topic")
                if t:
                    user_topics.add(t)
            lek = r.get("LastEvaluatedKey")
            if not lek:
                break

    out = []
    for it in items:
        gid = it["genre_id"]
        name = it.get("Name", "")
        is_sub = gid in user_topics
        out.append({"id": gid, "name": name, "isSubscribed": is_sub})

    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(out)}
