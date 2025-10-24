from pre_authorize import pre_authorize
from general_utils import response
from datetime import datetime
from zoneinfo import ZoneInfo
from read import get_feeds

def _choose_feed_index(num_pages: int, tz: str = "Europe/Belgrade") -> int:
    if num_pages <= 0: return 0
    hour = datetime.now(ZoneInfo(tz)).hour
    idx = int(hour * num_pages / 24)
    return min(idx, num_pages - 1)

@pre_authorize(['User'])
def lambda_handler(event, context):
    user_id = event["userId"]
    feeds = get_feeds(user_id) or []
    if not feeds:
        return response(200, {"artists": [], "albums": [], "songs": []})
    idx = _choose_feed_index(len(feeds))
    feed = feeds[idx] or {}
    return response(200, feed)
