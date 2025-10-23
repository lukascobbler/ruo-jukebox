from read import artist_releases, get_content, get_subscriptions_for_user
from general_utils import response, generate_s3_download_url
from pre_authorize import pre_authorize
import os

images_bucket = os.environ["IMAGES_BUCKET"]


@pre_authorize(['User'])
def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    artist_id = path_params.get("id")

    if not artist_id:
        return response(400, error="Missing artist ID")

    key = f"artists/{artist_id}.jpg"
    url = generate_s3_download_url(images_bucket, key)

    user_id = event["userId"]
    subs = get_subscriptions_for_user(user_id)

    subscribed_keys = {
        (row.get("sub_id") or row.get("SK"))
        for row in subs.get("artists", [])
        if row
    }

    is_sub = (("SUB~" + artist_id) in subscribed_keys) if artist_id else False

    artist = get_content(artist_id)
    artist["cover_url"] = url
    artist["isSubscribed"] = is_sub

    return response(200, {**artist, **artist_releases(artist_id)})
