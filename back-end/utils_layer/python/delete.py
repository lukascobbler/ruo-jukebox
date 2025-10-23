from boto3.dynamodb.conditions import Key
from read import query_all
import boto3
import os

dynamodb = boto3.resource("dynamodb")
interactions_table = dynamodb.Table(os.environ["INTERACTIONS_TABLE"])
userdata_table = dynamodb.Table(os.environ["USERDATA_TABLE"])
content_table = dynamodb.Table(os.environ["CONTENT_TABLE"])
feed_table = dynamodb.Table(os.environ["FEED_TABLE"])


def delete_genre(genre_id):
    # delete the genre meta and all linked content
    items = query_all(content_table, KeyConditionExpression=Key("PK").eq(genre_id))
    with content_table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})

    # remove genre reference from all artists, albums, singles, songs
    linked = query_all(content_table, IndexName="byType", KeyConditionExpression=Key("content_type").is_in(["ARTIST", "ALBUM", "SINGLE", "SONG"]))
    with content_table.batch_writer() as batch:
        for i in linked:
            if "genres" in i and any(g["genre_id"] == genre_id for g in i["genres"]):
                i["genres"] = [g for g in i["genres"] if g["genre_id"] != genre_id]
                batch.put_item(Item=i)


def delete_artist(artist_id):
    # delete the artist meta and all related content links
    items = query_all(content_table, KeyConditionExpression=Key("PK").eq(artist_id))
    with content_table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})

    # remove artist reference from songs, singles, albums
    linked = query_all(content_table, IndexName="byType", KeyConditionExpression=Key("content_type").is_in(["SONG", "ALBUM", "SINGLE"]))
    with content_table.batch_writer() as batch:
        for i in linked:
            if "artists" in i and any(a["artist_id"] == artist_id for a in i["artists"]):
                i["artists"] = [a for a in i["artists"] if a["artist_id"] != artist_id]
                batch.put_item(Item=i)


def delete_song(album_or_single_id, pos, song_id):
    # delete the core song entry
    content_table.delete_item(Key={"PK": album_or_single_id, "SK": f"POS~{pos}~{song_id}"})

    # delete all artist and genre cross-links
    artists = query_all(content_table, KeyConditionExpression=Key("SK").eq(f"CONTENT~{song_id}"))
    with content_table.batch_writer() as batch:
        for i in artists:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})


def delete_album(album_id):
    # delete META and all POS~ song items
    items = query_all(content_table, KeyConditionExpression=Key("PK").eq(album_id))
    with content_table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})

    # delete all artist and genre cross-links
    linked = query_all(content_table, KeyConditionExpression=Key("SK").eq(f"CONTENT~{album_id}"))
    with content_table.batch_writer() as batch:
        for i in linked:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})


def delete_single(single_id):
    # get single META to access artists and genres
    res = content_table.get_item(Key={"PK": single_id, "SK": "META"})
    item = res.get("Item")
    if not item:
        return {"error": "Single not found"}

    artists = item.get("artists", [])
    genres = item.get("genres", [])

    # delete all SINGLE items (META + POS~ entries)
    singles = query_all(content_table, KeyConditionExpression=Key("PK").eq(single_id))
    with content_table.batch_writer() as batch:
        for i in singles:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})

    # delete all artist and genre cross-links
    linked = []

    for artist in artists:
        res = content_table.query(KeyConditionExpression=Key("PK").eq(artist["artist_id"]) & Key("SK").eq(f"CONTENT~{single_id}"))
        linked.extend(res.get("Items", []))

    for genre in genres:
        res = content_table.query(KeyConditionExpression=Key("PK").eq(genre["genre_id"]) & Key("SK").eq(f"CONTENT~{single_id}"))
        linked.extend(res.get("Items", []))

    with content_table.batch_writer() as batch:
        for i in linked:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})


def delete_user(user_id):
    # delete user meta and all userdata (ratings, playlists, subs)
    items = query_all(userdata_table, KeyConditionExpression=Key("user_id").eq(user_id))
    with userdata_table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"user_id": i["user_id"], "SK": i["SK"]})


def delete_playlist(user_id, playlist_id):
    # delete playlist meta and all playlist items
    items = query_all(userdata_table, KeyConditionExpression=Key("user_id").eq(user_id) & Key("SK").begins_with(playlist_id))
    with userdata_table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"user_id": i["user_id"], "SK": i["SK"]})


def delete_playlist_item(user_id, playlist_id, pos, song_id):
    userdata_table.delete_item(Key={"user_id": user_id, "SK": f"{playlist_id}~POS~{pos}~{song_id}"})


def delete_rating(user_id, song_id):
    userdata_table.delete_item(Key={"user_id": user_id, "SK": f"RATING~{song_id}"})


def delete_subscription(user_id, target_id):
    sub_id = f"SUB~{target_id}"
    userdata_table.delete_item(Key={"user_id": user_id, "SK": sub_id})


def delete_interaction(user_id, ts):
    userdata_table.delete_item(Key={"user_id": user_id, "ts": str(ts)})


def delete_feed_item(user_id, content_id):
    userdata_table.delete_item(Key={"user_id": user_id, "content_id": content_id})
