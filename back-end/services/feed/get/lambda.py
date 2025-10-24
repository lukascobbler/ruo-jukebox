from pre_authorize import pre_authorize
from general_utils import response
from read import get_feed, get_contents
import json
from datetime import datetime
from zoneinfo import ZoneInfo

def _choose_feed_index(num_pages: int, tz: str = "Europe/Belgrade") -> int:
    if num_pages <= 0:
        return 0
    hour = datetime.now(ZoneInfo(tz)).hour
    idx = int(hour * num_pages / 24)
    return min(idx, num_pages - 1)

@pre_authorize(['User'])
def lambda_handler(event, context):
    user_id = event["userId"]
    feeds = get_feed(user_id) or []
    if not feeds:
        return response(200, {"artists": [], "albums": [], "songs": []})
    i = _choose_feed_index(len(feeds))
    feed = feeds[i] or {}
    albums_meta  = get_contents(feed.get("albums", []))
    artists_meta = get_contents(feed.get("artists", []))
    singles_meta = get_contents(feed.get("songs", []))
    result = {
        "albums":  albums_meta,
        "artists": artists_meta,
        "songs": singles_meta,
    }
    return response(200, result)
