from general_utils import response, generate_s3_upload_url
from pre_authorize import pre_authorize
from datetime import datetime
from zoneinfo import ZoneInfo
from read import get_feeds
import os

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]


def _choose_feed_index(num_pages: int, tz: str = "Europe/Belgrade") -> int:
    if num_pages <= 0:
        return 0
    hour = datetime.now(ZoneInfo(tz)).hour
    idx = int(hour * num_pages / 24)
    return min(idx, num_pages - 1)


def _insert_media_urls(data):
    if isinstance(data, dict):
        if "cover_key" in data:
            data["cover_url"] = generate_s3_upload_url(IMAGES_BUCKET, data["cover_key"])
        if "audio_key" in data:
            data["audio_url"] = generate_s3_upload_url(AUDIO_BUCKET, data["audio_key"])
        for v in data.values():
            _insert_media_urls(v)
    elif isinstance(data, list):
        for item in data:
            _insert_media_urls(item)
    return data


@pre_authorize(['User'])
def lambda_handler(event, context):
    user_id = event["userId"]
    feeds = get_feeds(user_id) or []
    if not feeds:
        return response(200, {"artists": [], "albums": [], "songs": []})
    idx = _choose_feed_index(len(feeds))
    feed = feeds[idx] or {}
    feed = _insert_media_urls(feed)
    return response(200, feed)
