import uuid, time


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
def create_song(table, album_or_single_id, songs: list[dict]):
    with table.batch_writer() as batch:
        for pos, song in enumerate(songs):
            song_id = f"SONG~{uuid.uuid4()}"
            batch.put_item(Item={**song, "PK": album_or_single_id, "SK": f"POS~{pos}~{song_id}"})
            for a in song["artists"]:
                batch.put_item(Item={**song, "PK": a["artist_id"], "SK": f"CONTENT~{song_id}"})
            for g in song["genres"]:
                batch.put_item(Item={**song, "PK": g["genre_id"], "SK": f"CONTENT~{song_id}"})


def create_album(table, name, artists, genres):
    album_id = f"ALBUM~{uuid.uuid4()}"
    core_album = {
        "content_id": album_id,
        "content_type": "ALBUM",
        "name": name,
        "name_lc": name.lower(),
        "cover_key": f"albums/{album_id}.jpg",
        "artists": artists,
        "genres": genres
    }

    with table.batch_writer() as batch:
        batch.put_item(Item={**core_album, "PK": album_id, "SK": "META"})
        for a in artists:
            batch.put_item(Item={**core_album, "PK": a["artist_id"], "SK": f"CONTENT~{album_id}"})
        for g in genres:
            batch.put_item(Item={**core_album, "PK": g["genre_id"], "SK": f"CONTENT~{album_id}"})

    return core_album


def create_single(table, name, artists, genres):
    single_id = f"SINGLE~{uuid.uuid4()}"
    core_single = {
        "content_id": single_id,
        "content_type": "SINGLE",
        "name": name,
        "name_lc": name.lower(),
        "cover_key": f"singles/{single_id}.jpg",
        "artists": artists,
        "genres": genres
    }

    with table.batch_writer() as batch:
        batch.put_item(Item={**core_single, "PK": single_id, "SK": "META"})
        for a in artists:
            batch.put_item(Item={**core_single, "PK": a["artist_id"], "SK": f"CONTENT~{single_id}"})
        for g in genres:
            batch.put_item(Item={**core_single, "PK": g["genre_id"], "SK": f"CONTENT~{single_id}"})

    return core_single


def create_artist(table, name, biography, genres):
    artist_id = f"ARTIST~{uuid.uuid4()}"
    core_artist = {
        "artist_id": artist_id,
        "content_type": "ARTIST",
        "name": name,
        "name_lc": name.lower(),
        "biography": biography,
        "cover_key": f"artists/{artist_id}.jpg",
        "genres": genres
    }

    with table.batch_writer() as batch:
        batch.put_item(Item={**core_artist, "PK": artist_id, "SK": "META"})
        for g in genres:
            batch.put_item(Item={**core_artist, "PK": g["genre_id"], "SK": f"CONTENT~{artist_id}"})

    return core_artist


def create_genre(table, name):
    genre_id = f"GENRE~{uuid.uuid4()}"
    core_genre = {
        "PK": genre_id,
        "SK": "META",
        "genre_id": genre_id,
        "content_type": "GENRE",
        "name": name
    }
    table.put_item(Item=core_genre)
    return core_genre


def create_user(table, name, surname, email, birthday):
    item = {
        "user_id": f"USER~{uuid.uuid4()}",
        "SK": "META",
        "name": name,
        "surname": surname,
        "email": email,
        "birthday": birthday
    }
    table.put_item(Item=item)
    return item


def create_playlist(table, user_id, name):
    playlist_id = f"PLAYLIST~{uuid.uuid4()}"
    item = {
        "user_id": user_id,
        "SK": f"{playlist_id}~CONTENT",
        "playlist_id": playlist_id,
        "name": name
    }
    table.put_item(Item=item)
    return item


def create_playlist_item(table, user_id, playlist_id, pos, song_id):
    item = {
        "user_id": user_id,
        "SK": f"{playlist_id}~POS~{pos}~{song_id}",
        "playlist_id": playlist_id
    }
    table.put_item(Item=item)
    return item


def create_rating(table, user_id, song_id, rating):
    item = {
        "user_id": user_id,
        "SK": f"RATING~{song_id}",
        "song_id": song_id,
        "rating": str(rating)
    }
    table.put_item(Item=item)
    return item


def create_subscription(table, user_id, target_type, target_id):
    sub_id = f"SUB~{target_type}~{target_id}"
    item = {
        "user_id": user_id,
        "SK": sub_id,
        "sub_id": sub_id
    }
    table.put_item(Item=item)
    return item


def create_interaction(table, user_id, artist_id=None, album_id=None, song_id=None, ttl_hours=24):
    ts = int(time.time())
    ttl = ts + ttl_hours * 3600
    item = {
        "user_id": user_id,
        "ts": str(ts),
        "ttl": ttl
    }
    if artist_id: item["artist_id"] = artist_id
    if album_id: item["album_id"] = album_id
    if song_id: item["song_id"] = song_id
    table.put_item(Item=item)
    return item


def create_feed_item(table, user_id, content_id):
    item = {
        "user_id": user_id,
        "content_id": content_id
    }
    table.put_item(Item=item)
    return item
