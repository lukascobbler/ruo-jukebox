import boto3, uuid, time, os

dynamodb = boto3.resource("dynamodb")
interactions_table = dynamodb.Table(os.environ["INTERACTIONS_TABLE"])
userdata_table = dynamodb.Table(os.environ["USERDATA_TABLE"])
content_table = dynamodb.Table(os.environ["CONTENT_TABLE"])
feed_table = dynamodb.Table(os.environ["FEED_TABLE"])


# song = {
#     "content_id": song_id,
#     "content_type": "SONG",
#     "name": name,
#     "name_lc": name.lower(),
#     "audio_key": f"songs/{song_id}.mp3",
#     "cover_key": cover_key,
#     "transcription_key": transcription_key,
#     "artists": artists,
#     "genres": genres
# }
def create_songs(album_or_single_id, songs: list[dict]):
    with content_table.batch_writer() as batch:
        for pos, song in enumerate(songs):
            song_id = song["content_id"]
            batch.put_item(Item={**song, "PK": album_or_single_id, "SK": f"POS~{pos}~{song_id}"})
            for a in song["artists"]:
                batch.put_item(Item={**song, "PK": a["artist_id"], "SK": f"CONTENT~{song_id}"})
            for g in song["genres"]:
                batch.put_item(Item={**song, "PK": g["genre_id"], "SK": f"CONTENT~{song_id}"})


def create_album(album_id, name, artists, genres):
    core_album = {
        "content_id": album_id,
        "content_type": "ALBUM",
        "name": name,
        "name_lc": name.lower(),
        "cover_key": f"albums/{album_id}.jpg",
        "artists": artists,
        "genres": genres
    }

    with content_table.batch_writer() as batch:
        batch.put_item(Item={**core_album, "PK": album_id, "SK": "META"})
        for a in artists:
            batch.put_item(Item={**core_album, "PK": a["artist_id"], "SK": f"CONTENT~{album_id}"})
        for g in genres:
            batch.put_item(Item={**core_album, "PK": g["genre_id"], "SK": f"CONTENT~{album_id}"})

    return core_album


def create_single(single_id, name, artists, genres):
    core_single = {
        "content_id": single_id,
        "content_type": "SINGLE",
        "name": name,
        "name_lc": name.lower(),
        "cover_key": f"singles/{single_id}.jpg",
        "artists": artists,
        "genres": genres
    }

    with content_table.batch_writer() as batch:
        batch.put_item(Item={**core_single, "PK": single_id, "SK": "META"})
        for a in artists:
            batch.put_item(Item={**core_single, "PK": a["artist_id"], "SK": f"CONTENT~{single_id}"})
        for g in genres:
            batch.put_item(Item={**core_single, "PK": g["genre_id"], "SK": f"CONTENT~{single_id}"})

    return core_single


def create_artist(artist_id, name, biography, genres):
    core_artist = {
        "artist_id": artist_id,
        "content_type": "ARTIST",
        "name": name,
        "name_lc": name.lower(),
        "biography": biography,
        "cover_key": f"artists/{artist_id}.jpg",
        "genres": genres
    }

    with content_table.batch_writer() as batch:
        batch.put_item(Item={**core_artist, "PK": artist_id, "SK": "META"})
        for g in genres:
            batch.put_item(Item={**core_artist, "PK": g["genre_id"], "SK": f"CONTENT~{artist_id}"})

    return core_artist


def create_genre(genre_id, name):
    core_genre = {
        "PK": genre_id,
        "SK": "META",
        "genre_id": genre_id,
        "content_type": "GENRE",
        "name": name
    }
    content_table.put_item(Item=core_genre)
    return core_genre


def create_user(user_id, name, surname, email, birthday):
    item = {
        "user_id": user_id,
        "SK": "META",
        "name": name,
        "surname": surname,
        "email": email,
        "birthday": birthday
    }
    userdata_table.put_item(Item=item)
    return item


def create_playlist(playlist_id, user_id, name):
    item = {
        "user_id": user_id,
        "SK": f"{playlist_id}~CONTENT",
        "playlist_id": playlist_id,
        "name": name
    }
    userdata_table.put_item(Item=item)
    return item


def create_playlist_item(user_id, playlist_id, pos, song_id):
    item = {
        "user_id": user_id,
        "SK": f"{playlist_id}~POS~{pos}~{song_id}",
        "playlist_id": playlist_id
    }
    userdata_table.put_item(Item=item)
    return item


def create_rating(user_id, song_id, rating):
    item = {
        "user_id": user_id,
        "SK": f"RATING~{song_id}",
        "rating_user": f"{str(rating)}~{user_id}",
        "song_id": song_id,
        "rating": str(rating)
    }
    userdata_table.put_item(Item=item)
    return item


def create_subscription(user_id, target_id):
    sub_id = f"SUB~{target_id}"
    item = {
        "user_id": user_id,
        "SK": sub_id,
        "sub_id": sub_id
    }
    userdata_table.put_item(Item=item)
    return item


def create_interaction(user_id, artist_id=None, album_id=None, song_id=None, ttl_hours=24):
    ts = int(time.time())
    ttl = ts + ttl_hours * 3600
    item = {"user_id": user_id, "ts": str(ts), "ttl": ttl}
    if artist_id: item["artist_id"] = artist_id
    if album_id: item["album_id"] = album_id
    if song_id: item["song_id"] = song_id
    interactions_table.put_item(Item=item)
    return item


def create_feed_item(user_id, content_id):
    item = {"user_id": user_id, "content_id": content_id}
    feed_table.put_item(Item=item)
    return item
