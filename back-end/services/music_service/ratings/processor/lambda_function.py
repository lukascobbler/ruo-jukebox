import os, json, boto3
dynamodb = boto3.resource("dynamodb")
TRACKS = dynamodb.Table(os.environ["TRACKS_TABLE"])

def lambda_handler(event, context):
    for rec in event["Records"]:
        msg = json.loads(rec["body"])
        t = msg.get("type")
        track_id = msg.get("track_id")
        rating = int(msg.get("rating",0))
        if t == "RATING_INC":
            TRACKS.update_item(
                Key={"track_id": track_id},
                UpdateExpression=f"ADD rating_{rating} :one",
                ExpressionAttributeValues={":one": 1}
            )
        elif t == "RATING_DEC":
            TRACKS.update_item(
                Key={"track_id": track_id},
                UpdateExpression=f"ADD rating_{rating} :neg",
                ExpressionAttributeValues={":neg": -1}
            )
