from pre_authorize import pre_authorize
from general_utils import response
from read import list_genres, get_subscriptions_for_user
import os, boto3

dynamodb = boto3.resource("dynamodb")
content_table = dynamodb.Table(os.environ["CONTENT_TABLE"])
userdata_table = dynamodb.Table(os.environ["USERDATA_TABLE"])

@pre_authorize(["Admin", "LoggedInUser"])
def lambda_handler(event, context):
    user_id = event["userId"]
    genres = list_genres(content_table)
    subs = get_subscriptions_for_user(userdata_table, user_id)
    
    subscribed_genre_ids = set()
    
    for item in subs.get("genres", []):
        sk = item.get("SK", "")  # "SUB~GENRE~<uuid>"
        parts = sk.split("~", 2)
        if len(parts) == 3:
            subscribed_genre_ids.add(f"GENRE~{parts[2]}")
    
    items = []
    for g in genres:
        # Prefer the explicit 'genre_id' field; fall back to PK if needed
        genre_id = g.get("genre_id") or g.get("PK")
        items.append({
            "genre_id": genre_id,
            "name": g.get("name"),
            "content_type": g.get("content_type"),
            "subscribed": genre_id in subscribed_genre_ids
        })
    return response(200, {"user_id": user_id, "items": items})