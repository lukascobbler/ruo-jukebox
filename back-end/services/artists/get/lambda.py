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

    user_id = event["userId"]
    subs = get_subscriptions_for_user(user_id)

    subscribed_keys = {
        (row.get("sub_id") or row.get("SK"))
        for row in subs.get("artists", [])
        if row
    }

    is_sub = (("SUB~" + artist_id) in subscribed_keys) if artist_id else False

    artist = get_content(artist_id)
    artist_content = artist_releases(artist_id)

    if "cover_key" in artist:
        artist["cover_url"] = generate_s3_download_url(images_bucket, artist["cover_key"])

    for album in artist_content["albums"]:
        if "cover_key" in album:
            album["cover_url"] = generate_s3_download_url(images_bucket, album["cover_key"])

    for single in artist_content["singles"]:
        if "cover_key" in single:
            single["cover_url"] = generate_s3_download_url(images_bucket, single["cover_key"])

    artist["isSubscribed"] = is_sub

    return response(200, {**artist, **artist_content})
