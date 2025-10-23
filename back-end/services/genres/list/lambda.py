from pre_authorize import pre_authorize
from read import get_subscriptions_for_user
from read import list_genres
from general_utils import response

@pre_authorize(["Admin", "User"])
def lambda_handler(event, context):
    user_id = event["userId"]
    subs = get_subscriptions_for_user(user_id)
    sub_genre_rows = subs.get("genres", [])
    genres = list_genres()
    items = []
    subscribed_keys = {
        (row.get("sub_id") or row.get("SK"))
        for row in sub_genre_rows
        if row
    }
    for g in genres:
        gid = g.get("genre_id") or g.get("PK")
        name = g.get("name")
        is_sub = (("SUB~" + gid) in subscribed_keys) if gid else False

        items.append({
            "genre_id": gid,
            "name": name,
            "isSubscribed": is_sub
        })

    return response(200, items)
