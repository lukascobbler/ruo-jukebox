import os, json
import boto3
from pre_authorize import pre_authorize
from read import get_subscriptions_for_user
from general_utils import response


dynamodb = boto3.resource("dynamodb")
userdata = dynamodb.Table(os.environ["USERDATA_TABLE"])

@pre_authorize(['Admin','LoggedInUser'])
def lambda_handler(event, context):
    user_id = event["userId"]
    subs = get_subscriptions_for_user(userdata, user_id)
    def _to_uuid(item):
        sk = item.get("SK", "")
        parts = sk.split("~", 2)  # ["SUB", "TYPE", "UUID"]
        return parts[2] if len(parts) >= 3 else sk
    result = {
        "user_id": user_id,
        "genres": [{"id": _to_uuid(i), "sk": i["SK"]} for i in subs.get("genres", [])],
        "artists": [{"id": _to_uuid(i), "sk": i["SK"]} for i in subs.get("artists", [])],
    }
    return response(200, result)