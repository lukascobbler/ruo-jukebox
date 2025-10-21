import os, json
import boto3
from botocore.exceptions import ClientError
from pre_authorize import pre_authorize

dynamodb = boto3.resource("dynamodb")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE,PATCH"
}

subs_table = dynamodb.Table(os.environ["SUBSCRIPTIONS_TABLE"])

@pre_authorize(['Admin','LoggedInUser'])
def lambda_handler(event, context):
    user_id = event.get("userId")
    topic = (event.get("pathParameters") or {}).get("topic")
    if not user_id or not topic:
        return {"statusCode": 400, "headers": CORS_HEADERS,
                "body": json.dumps({"message":"Missing user or topic"})}

    try:
        subs_table.delete_item(
            Key={"topic": topic, "user_id": user_id},
            ConditionExpression="attribute_exists(user_id)"
        )
        deleted = True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {"statusCode": 404, "headers": CORS_HEADERS, "body": json.dumps({"message":"Subscription not found"})}
        return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"message":"Failed to delete", "error": str(e)})}

    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"topic": topic, "deleted": deleted})}
