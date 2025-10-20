from botocore.exceptions import ClientError
from datetime import datetime, timezone
import json, os, boto3

ALBUMS_TABLE = os.environ.get("ALBUMS_TABLE")
CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))

dynamodb = boto3.resource("dynamodb")
albums_table = dynamodb.Table(ALBUMS_TABLE)


def lambda_handler(event, context):
    try:
        album_id = event.get("pathParameters", {}).get("id")
        if not album_id:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"message": "Missing album ID"})
            }

        albums_table.update_item(
            Key={"album_id": album_id},
            UpdateExpression="SET released = :r, released_at = :t",
            ExpressionAttributeValues={
                ":r": True,
                ":t": int(datetime.now(timezone.utc).timestamp())
            },
            ConditionExpression="attribute_exists(album_id)"
        )

        return {
            "statusCode": 204,
            "headers": CORS_HEADERS,
            "body": ""
        }

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({"message": "Album not found"})
            }

        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": f"DynamoDB error: {str(e)}"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": f"Internal server error: {str(e)}"})
        }
