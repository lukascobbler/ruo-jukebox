from read import get_interactions, get_rating, artists_all_content_feed, genre_all_content_feed, get_contents, songs_for_album, list_albums_n, list_artists_n, list_songs_n
from pre_authorize import pre_authorize
from general_utils import response
from create import create_feeds
from datetime import datetime
from zoneinfo import ZoneInfo

CONNECT_ENTITIES_MAXIMUM = 20
FINAL_ENTITIES_MINIMUM = 5
PERIODS_OF_DAY = 4


def _get_period_from_timestamp(timestamp: int, splits: int, tz: str = "Europe/Belgrade") -> int:
    if splits <= 0:
        return 0
    hour = datetime.fromtimestamp(timestamp, ZoneInfo(tz)).hour
    period = int(hour * splits / 24)
    return min(period, splits - 1)


def _preprocess_user_interactions(user_id: str, interactions: list):
    ts_values, result, seen = [], {}, set()
    for item in interactions:
        if "ts" in item:
            ts_values.append(int(item["ts"]))
        song_id = item.get("song_id")
        if song_id and song_id not in seen:
            seen.add(song_id)
            rating = get_rating(user_id, song_id)
            if isinstance(rating, list) and rating and "rating" in rating[0]:
                result[song_id] = rating[0]["rating"]
    return (min(ts_values), max(ts_values), result) if ts_values else (None, None, result)


def lambda_handler(event, context):
    for record in event.get("Records", []):
        user_id = record["body"]
        interactions = get_interactions(user_id)
        min_ts, max_ts, ratings = _preprocess_user_interactions(user_id, interactions)
        ts_diff = max_ts - min_ts

        seen = {
            "genres": {},
            "artists": {},
            "albums": {},
            "songs": {}
        }

        feeds = []

        for period in range(PERIODS_OF_DAY):
            for inter in interactions:
                ts = int(inter.get("ts", "0"))
                time_of_day = 1.5 if _get_period_from_timestamp(ts, PERIODS_OF_DAY) == period else 1
                freshness = 1 + (ts - min_ts) / ts_diff
                liking = 1 + int(ratings[inter["song_id"]]) if ("song_id" in inter) and inter["song_id"] in ratings else 1
                value = float(inter["value"]) * time_of_day * freshness * liking

                if "artist_id" in inter:
                    seen["artists"][inter["artist_id"]] = seen["artists"].get(inter["artist_id"], 0) + value
                if "album_id" in inter:
                    seen["albums"][inter["album_id"]] = seen["albums"].get(inter["album_id"], 0) + value
                if "genre_id" in inter:
                    seen["genres"][inter["genre_id"]] = seen["genres"].get(inter["genre_id"], 0) + value
                if "song_id" in inter:
                    seen["songs"][inter["song_id"]] = seen["songs"].get(inter["song_id"], 0) + value

            seen["artists"] = dict(sorted(seen["artists"].items(), key=lambda x: x[1], reverse=True)[CONNECT_ENTITIES_MAXIMUM:])
            seen["genres"] = dict(sorted(seen["genres"].items(), key=lambda x: x[1], reverse=True)[CONNECT_ENTITIES_MAXIMUM:])
            seen["songs"] = dict(sorted(seen["songs"].items(), key=lambda x: x[1], reverse=True)[CONNECT_ENTITIES_MAXIMUM:])
            seen["albums"] = dict(sorted(seen["albums"].items(), key=lambda x: x[1], reverse=True)[CONNECT_ENTITIES_MAXIMUM:])

            myb_seen = {
                "artists": [],
                "albums": [],
                "songs": []
            }

            for artist_id in seen["artists"]:
                content = artists_all_content_feed(artist_id)
                myb_seen["albums"] += content["albums"]
                myb_seen["songs"] += content["songs"]

            for genre_id in seen["genres"]:
                content = genre_all_content_feed(genre_id)
                myb_seen["artists"] += content["artists"]
                myb_seen["albums"] += content["albums"]
                myb_seen["songs"] += content["songs"]

            for song_id in seen["songs"]:
                content = get_contents(song_id)
                myb_seen["artists"] += content["artists"]
                myb_seen["albums"] += content["albums"]

            for album_id in seen["albums"]:
                content = get_contents(album_id)
                myb_seen["artists"] += content["artists"]
                songs = songs_for_album(album_id)
                myb_seen["songs"] += songs

            artists_missing = FINAL_ENTITIES_MINIMUM - len(myb_seen["artists"])
            albums_missing = FINAL_ENTITIES_MINIMUM - len(myb_seen["albums"])
            songs_missing = FINAL_ENTITIES_MINIMUM - len(myb_seen["songs"])

            if artists_missing > 0:
                myb_seen["artists"] += list_artists_n(artists_missing)
            if albums_missing > 0:
                myb_seen["albums"] += list_albums_n(albums_missing)
            if songs_missing > 0:
                myb_seen["songs"] += list_songs_n(songs_missing)

            feeds.append(myb_seen)

        create_feeds(user_id, feeds)
