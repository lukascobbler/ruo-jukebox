from general_utils import response, generate_s3_download_url
from read import artist_releases, get_content
from pre_authorize import pre_authorize
import os, json

images_bucket = os.environ["IMAGES_BUCKET"]


@pre_authorize(['User'])
def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    try:
        artist_id = body.get("artist_id")
    except KeyError:
        return response(400, error="Missing artist_id")

    key = f"artists/{artist_id}.jpg"
    url = generate_s3_download_url(key)
    artist = get_content(artist_id)

    return response(200, {"cover_url": url, **artist, **artist_releases(artist_id)})
