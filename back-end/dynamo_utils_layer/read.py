from boto3.dynamodb.conditions import Key, Attr


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


# all genres
def list_genres(table):
    return query_all(table, IndexName="byType", KeyConditionExpression=Key("content_type").eq("GENRE"), FilterExpression=Attr("SK").eq("META"))


# all artists
def list_artists(table):
    return query_all(table, IndexName="byType", KeyConditionExpression=Key("content_type").eq("ARTIST"), FilterExpression=Attr("SK").eq("META"))


# all singles
def list_singles(table):
    return query_all(table, IndexName="byType", KeyConditionExpression=Key("content_type").eq("SINGLE"), FilterExpression=Attr("SK").eq("META"))


# all albums
def list_albums(table):
    return query_all(table, IndexName="byType", KeyConditionExpression=Key("content_type").eq("ALBUM"), FilterExpression=Attr("SK").eq("META"))


# all albums and artists for a given genre (discovery page)
def list_by_genre(table, genre_id: str):  # e.g. 'GENRE~{UUID}'
    items = query_all(table, KeyConditionExpression=Key("PK").eq(genre_id) & Key("SK").begins_with("CONTENT~"))
    res = {"artists": [], "albums": []}
    for item in items:
        if item["SK"].startswith("CONTENT~ARTIST~"):
            res["artists"].append(item)
        elif item["SK"].startswith("CONTENT~ALBUM~"):
            res["albums"].append(item)
    return res


# all singles and albums of an artist (artist page)
def artist_releases(table, artist_id: str):  # e.g. 'ARTIST~{UUID}'
    items = query_all(table, KeyConditionExpression=Key("PK").eq(artist_id) & Key("SK").begins_with("CONTENT~"))
    res = {"singles": [], "albums": []}
    for item in items:
        if item["SK"].startswith("CONTENT~SINGLE~"):
            res["singles"].append(item)
        elif item["SK"].startswith("CONTENT~ALBUM~"):
            res["albums"].append(item)
    return res


# all songs for an album
def songs_for_album(table, album_id: str):
    return query_all(table, KeyConditionExpression=Key("PK").eq(album_id) & Key("SK").begins_with("POS~"))


# search
def search(table, query: str):
    items = query_all(table, IndexName="byName", KeyConditionExpression=Key("name_lc").eq(query.lower()))
    res = {"songs": [], "albums": [], "artists": []}
    for item in items:
        if item["SK"].startswith("CONTENT~SINGLE~"):
            res["singles"].append(item)
        elif item["SK"].startswith("CONTENT~ALBUM~"):
            res["albums"].append(item)
        elif item["SK"].startswith("CONTENT~ARTIST~"):
            res["artists"].append(item)
    return res


# all genres and artists a user is subscribed to
def get_subscriptions_for_user(table, user_id: str):  # e.g. 'USER~{UUID}'
    items = query_all(table, KeyConditionExpression=Key("PK").eq(user_id) & Key("SK").begins_with("SUB~"))
    res = {"genres": [], "artists": []}
    for item in items:
        if item["SK"].startswith("SUB~GENRE~"):
            res["genres"].append(item)
        elif item["SK"].startswith("SUB~ARTIST~"):
            res["artists"].append(item)
    return res


# all users subscribed to a genre or artist
def get_users_for_subscription(table, topic_id: str):  # e.g. 'GENRE~{UUID}' or 'ARTIST~{UUID}'
    return query_all(table, IndexName="getSubscribed", KeyConditionExpression=Key("sub_id").eq(f"SUB~{topic_id}"))


# rating from user for song
def get_rating(table, user_id: str, song_id: str):
    return query_all(table, KeyConditionExpression=Key("user_id").eq(user_id) & Key("SK").begins_with(f"RATING~{song_id}"))


# rating for a song
def get_rating_by_song(table, song_id: str):
    return query_all(table, IndexName="ratingBySong", KeyConditionExpression=Key("song_id").eq(song_id))
