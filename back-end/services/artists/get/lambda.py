from general_utils import response, generate_s3_download_url
from read import artist_releases, get_content
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

    artist = get_content(artist_id)
    artist["cover_url"] = url

    return response(200, {**artist, **artist_releases(artist_id)})
