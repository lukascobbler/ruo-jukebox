import boto3, os, re, uuid
from boto3.dynamodb.conditions import Key

STACK_NAME = "DynamoDbStack"

cf = boto3.client("cloudformation", region_name=os.getenv("CDK_DEFAULT_REGION", "eu-central-1"))
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("CDK_DEFAULT_REGION", "eu-central-1"))


def get_table_name(stack_name, logical_prefix):
    resp = cf.describe_stack_resources(StackName=stack_name)
    for r in resp["StackResources"]:
        if r["ResourceType"] == "AWS::DynamoDB::Table" and r["LogicalResourceId"].startswith(logical_prefix):
            return r["PhysicalResourceId"]
    raise RuntimeError(f"No table found with logical ID starting with {logical_prefix}")


genres_table = dynamodb.Table(get_table_name(STACK_NAME, "Genres"))


def clear_genres_table():
    deleted = 0
    last_key = None
    while True:
        params = {
            "KeyConditionExpression": Key("PK").eq("genres"),
            "ProjectionExpression": "genre_id, #n",
            "ExpressionAttributeNames": {"#n": "name"}
        }
        if last_key:
            params["ExclusiveStartKey"] = last_key
        resp = genres_table.query(**params)
        items = resp.get("Items", [])
        if not items:
            break
        with genres_table.batch_writer() as batch:
            for i in items:
                print(i)
                batch.delete_item(Key={"genre_id": i["genre_id"]})
        deleted += len(items)
        last_key = resp.get("LastEvaluatedKey")
        if not last_key:
            break
    print(f"Deleted {deleted} items.")


def seed_genres():
    genres = ["Rock", "Pop", "Jazz", "Blues", "Classical", "Electronic", "Hip-Hop", "Metal", "Latin", "Soul", "Country", "Reggae"]
    print("Inserting genres...")
    with genres_table.batch_writer() as batch:
        for name in genres:
            batch.put_item(Item={
                "PK": "genres",
                "genre_id": f"GENRE~{uuid.uuid4()}",
                "name": name,
            })
    print(f"Inserted {len(genres)} genres.")


if __name__ == "__main__":
    clear_genres_table()
    seed_genres()
    print("Genres table reset complete.")
