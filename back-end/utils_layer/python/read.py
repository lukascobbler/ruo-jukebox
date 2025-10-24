from boto3.dynamodb.conditions import Key
import boto3
import os

dynamodb = boto3.resource("dynamodb")
interactions_table = dynamodb.Table(os.environ["INTERACTIONS_TABLE"])
userdata_table = dynamodb.Table(os.environ["USERDATA_TABLE"])
content_table = dynamodb.Table(os.environ["CONTENT_TABLE"])
feed_table = dynamodb.Table(os.environ["FEED_TABLE"])


def query_all(table, **kwargs):
    items, start_key = [], None
    while True:
        if start_key:
            kwargs["ExclusiveStartKey"] = start_key
        resp = table.query(**kwargs)
        items.extend(resp.get("Items", []))
        start_key = resp.get("LastEvaluatedKey")
        if not start_key:
            break
    return items


def query_n(table, limit, **kwargs):
    items, start_key = [], None
    while len(items) < limit:
        if start_key:
            kwargs["ExclusiveStartKey"] = start_key
        resp = table.query(**kwargs)
        items.extend(resp.get("Items", []))
        if len(items) >= limit or "LastEvaluatedKey" not in resp:
            break
        start_key = resp["LastEvaluatedKey"]
    return items[:limit]


def batch_get_items(table, keys):
    client = table.meta.client
    results = []
    for i in range(0, len(keys), 100):
        req = {table.name: {"Keys": keys[i:i + 100]}}
        while req:
            resp = client.batch_get_item(RequestItems=req)
            results += resp["Responses"].get(table.name, [])
            req = resp.get("UnprocessedKeys")
    return results


# get content with id
def get_content(content_id: str):
    return query_all(content_table, KeyConditionExpression=Key("PK").eq(content_id) & Key("SK").eq("META"))[0]


# get batch content by id
def get_contents(content_ids: list[str]):
    keys = [{"PK": cid, "SK": "META"} for cid in content_ids]
    return batch_get_items(content_table, keys)


# all genres
def list_genres():
    return query_all(content_table, IndexName="byType", KeyConditionExpression=Key("content_type").eq("GENRE") & Key("SK").eq("META"))


# all artists
def list_artists():
    return query_all(content_table, IndexName="byType", KeyConditionExpression=Key("content_type").eq("ARTIST") & Key("SK").eq("META"))


# all singles
def list_singles():
    return query_all(content_table, IndexName="byType", KeyConditionExpression=Key("content_type").eq("SINGLE") & Key("SK").eq("META"))


# all albums
def list_albums():
    return query_all(content_table, IndexName="byType", KeyConditionExpression=Key("content_type").eq("ALBUM") & Key("SK").eq("META"))


def list_artists_n(n):
    return query_n(content_table, n, IndexName="byType", KeyConditionExpression=Key("content_type").eq("ARTIST") & Key("SK").eq("META"))


def list_albums_n(n):
    return query_n(content_table, n, IndexName="byType", KeyConditionExpression=Key("content_type").eq("ALBUM") & Key("SK").eq("META"))


def list_songs_n(n):
    return query_n(content_table, n, IndexName="byType", KeyConditionExpression=Key("content_type").eq("SONG") & Key("SK").eq("META"))


# all albums and artists for a given genre (discovery page)
def list_by_genre(genre_id: str):  # e.g. 'GENRE~{UUID}'
    items = query_all(content_table, KeyConditionExpression=Key("PK").eq(genre_id) & Key("SK").begins_with("CONTENT~"))
    res = {"artists": [], "albums": []}
    for item in items:
        if item["SK"].startswith("CONTENT~ARTIST~"):
            res["artists"].append(item)
        elif item["SK"].startswith("CONTENT~ALBUM~"):
            res["albums"].append(item)
    return res


# all singles and albums of an artist (artist page)
def artist_releases(artist_id: str):  # e.g. 'ARTIST~{UUID}'
    items = query_all(content_table, KeyConditionExpression=Key("PK").eq(artist_id) & Key("SK").begins_with("CONTENT~"))
    res = {"singles": [], "albums": []}
    for item in items:
        if item["SK"].startswith("CONTENT~SINGLE~"):
            res["singles"].append(item)
        elif item["SK"].startswith("CONTENT~ALBUM~"):
            res["albums"].append(item)
    return res


def artists_all_content_feed(artist_id: str):  # e.g. 'ARTIST~{UUID}'
    items = query_all(content_table, KeyConditionExpression=Key("PK").eq(artist_id) & Key("SK").begins_with("CONTENT~"))
    res = {"songs": [], "albums": []}
    for item in items:
        if item["SK"].startswith("CONTENT~SONG~"):
            res["songs"].append(item)
        elif item["SK"].startswith("CONTENT~ALBUM~"):
            res["albums"].append(item)
    return res


def genre_all_content_feed(genre_id: str):  # e.g. 'GENRE~{UUID}'
    items = query_all(content_table, KeyConditionExpression=Key("PK").eq(genre_id) & Key("SK").begins_with("CONTENT~"))
    res = {"artists": [], "albums": [], "songs": []}
    for item in items:
        if item["SK"].startswith("CONTENT~ARTIST~"):
            res["artists"].append(item)
        elif item["SK"].startswith("CONTENT~ALBUM~"):
            res["albums"].append(item)
        elif item["SK"].startswith("CONTENT~SONG~"):
            res["songs"].append(item)
    return res


# all songs for an album
def songs_for_album(album_id: str):
    return query_all(content_table, KeyConditionExpression=Key("PK").eq(album_id) & Key("SK").begins_with("POS~"))


# search
def search(query: str):
    items = query_all(content_table, IndexName="byName", KeyConditionExpression=Key("name_lc").eq(query.lower()))
    res = {"songs": [], "albums": [], "artists": []}
    for item in items:
        if item["content_type"].startswith("SONG"):
            res["songs"].append(item)
        elif item["content_type"].startswith("ALBUM"):
            res["albums"].append(item)
        elif item["content_type"].startswith("ARTIST"):
            res["artists"].append(item)
    return res


# all genres and artists a user is subscribed to
def get_subscriptions_for_user(user_id: str):  # e.g. 'USER~{UUID}'
    items = query_all(userdata_table, KeyConditionExpression=Key("user_id").eq(user_id) & Key("SK").begins_with("SUB~"))
    res = {"genres": [], "artists": []}
    for item in items:
        if item["SK"].startswith("SUB~GENRE~"):
            res["genres"].append(item)
        elif item["SK"].startswith("SUB~ARTIST~"):
            res["artists"].append(item)
    return res


# all genres and artists a user is subscribed to
def get_subscriptions_for_user_sub_page(user_id: str):  # e.g. 'USER~{UUID}'
    items = query_all(userdata_table, KeyConditionExpression=Key("user_id").eq(user_id) & Key("SK").begins_with("SUB~"))
    res = {"genres": [], "artists": []}
    for item in items:
        item_id = item["SK"].lstrip("SUB~")
        if item["SK"].startswith("SUB~GENRE~"):
            res["genres"].append(item_id)
        elif item["SK"].startswith("SUB~ARTIST~"):
            res["artists"].append(item_id)
    res["genres"] = get_contents(res["genres"])
    res["artists"] = get_contents(res["artists"])
    return res


# all users subscribed to a genre or artist
def get_users_for_subscription(topic_id: str):  # e.g. 'GENRE~{UUID}' or 'ARTIST~{UUID}'
    return query_all(userdata_table, IndexName="getSubscribed", KeyConditionExpression=Key("sub_id").eq(f"SUB~{topic_id}"))


# rating from user for song
def get_rating(user_id: str, song_id: str):
    return query_all(userdata_table, KeyConditionExpression=Key("user_id").eq(user_id) & Key("SK").begins_with(f"RATING~{song_id}"))


# rating for a song
def get_rating_by_song(song_id: str):
    return query_all(userdata_table, IndexName="ratingBySong", KeyConditionExpression=Key("song_id").eq(song_id))


# read from feed
def get_feeds(user_id: str):
    items = query_all(feed_table, KeyConditionExpression=Key("user_id").eq(user_id))
    if not items:
        return []
    for it in items:
        if "feeds" in it and isinstance(it["feeds"], list):
            return it["feeds"]
    return []


def get_interactions(user_id: str):
    return query_all(interactions_table, KeyConditionExpression=Key("user_id").eq(user_id))
