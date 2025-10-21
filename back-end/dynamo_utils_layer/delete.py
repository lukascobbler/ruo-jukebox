from boto3.dynamodb.conditions import Key
from read import query_all

def delete_genre(table, genre_id):
    # delete the genre meta and all linked content
    items = query_all(table, KeyConditionExpression=Key("PK").eq(genre_id))
    with table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})

    # remove genre reference from all artists, albums, singles, songs
    linked = query_all(table, IndexName="byType", KeyConditionExpression=Key("content_type").is_in(["ARTIST", "ALBUM", "SINGLE", "SONG"]))
    with table.batch_writer() as batch:
        for i in linked:
            if "genres" in i and any(g["genre_id"] == genre_id for g in i["genres"]):
                i["genres"] = [g for g in i["genres"] if g["genre_id"] != genre_id]
                batch.put_item(Item=i)


def delete_artist(table, artist_id):
    # delete the artist meta and all related content links
    items = query_all(table, KeyConditionExpression=Key("PK").eq(artist_id))
    with table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})

    # remove artist reference from songs, singles, albums
    linked = query_all(table, IndexName="byType", KeyConditionExpression=Key("content_type").is_in(["SONG", "ALBUM", "SINGLE"]))
    with table.batch_writer() as batch:
        for i in linked:
            if "artists" in i and any(a["artist_id"] == artist_id for a in i["artists"]):
                i["artists"] = [a for a in i["artists"] if a["artist_id"] != artist_id]
                batch.put_item(Item=i)


def delete_song(table, album_or_single_id, pos, song_id):
    # delete the core song entry
    table.delete_item(Key={"PK": album_or_single_id, "SK": f"POS~{pos}~{song_id}"})

    # delete all artist and genre cross-links
    artists = query_all(table, KeyConditionExpression=Key("SK").eq(f"CONTENT~{song_id}"))
    with table.batch_writer() as batch:
        for i in artists:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})


def delete_album(table, album_id):
    # delete META and all POS~ song items
    items = query_all(table, KeyConditionExpression=Key("PK").eq(album_id))
    with table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})

    # delete all artist and genre cross-links
    linked = query_all(table, KeyConditionExpression=Key("SK").eq(f"CONTENT~{album_id}"))
    with table.batch_writer() as batch:
        for i in linked:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})


def delete_single(table, single_id):
    # delete META
    items = query_all(table, KeyConditionExpression=Key("PK").eq(single_id))
    with table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})

    # delete all artist and genre cross-links
    linked = query_all(table, KeyConditionExpression=Key("SK").eq(f"CONTENT~{single_id}"))
    with table.batch_writer() as batch:
        for i in linked:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})


def delete_user(table, user_id):
    # delete user meta and all userdata (ratings, playlists, subs)
    items = query_all(table, KeyConditionExpression=Key("user_id").eq(user_id))
    with table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"user_id": i["user_id"], "SK": i["SK"]})


def delete_playlist(table, user_id, playlist_id):
    # delete playlist meta and all playlist items
    items = query_all(table, KeyConditionExpression=Key("user_id").eq(user_id) & Key("SK").begins_with(playlist_id))
    with table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"user_id": i["user_id"], "SK": i["SK"]})


def delete_playlist_item(table, user_id, playlist_id, pos, song_id):
    table.delete_item(Key={"user_id": user_id, "SK": f"{playlist_id}~POS~{pos}~{song_id}"})


def delete_rating(table, user_id, song_id):
    table.delete_item(Key={"user_id": user_id, "SK": f"RATING~{song_id}"})


def delete_subscription(table, user_id, target_type, target_id):
    sub_id = f"SUB~{target_type}~{target_id}"
    table.delete_item(Key={"user_id": user_id, "SK": sub_id})


def delete_interaction(table, user_id, ts):
    table.delete_item(Key={"user_id": user_id, "ts": str(ts)})


def delete_feed_item(table, user_id, content_id):
    table.delete_item(Key={"user_id": user_id, "content_id": content_id})
