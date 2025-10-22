from boto3.dynamodb.conditions import Key
from read import query_all
import boto3
import os

dynamodb = boto3.resource("dynamodb")
interactions_table = dynamodb.Table(os.environ["INTERACTIONS_TABLE"])
userdata_table = dynamodb.Table(os.environ["USERDATA_TABLE"])
content_table = dynamodb.Table(os.environ["CONTENT_TABLE"])
feed_table = dynamodb.Table(os.environ["FEED_TABLE"])


def update_genre(genre_id, name):
    content_table.update_item(
        Key={"PK": genre_id, "SK": "META"},
        UpdateExpression="SET #n = :n",
        ExpressionAttributeNames={"#n": "name"},
        ExpressionAttributeValues={":n": name}
    )

    items = query_all(content_table, KeyConditionExpression=Key("PK").eq(genre_id) & Key("SK").begins_with("CONTENT~"))
    with content_table.batch_writer() as batch:
        for i in items:
            if "genres" in i:
                i["genres"] = [{**g, "name": name} if g["genre_id"] == genre_id else g for g in i["genres"]]
                batch.put_item(Item=i)


def update_artist(artist_id, name=None, biography=None, genres=None):
    artist = content_table.get_item(Key={"PK": artist_id, "SK": "META"}).get("Item")
    if not artist:
        return None

    expr, names, vals = [], {}, {}
    if name:
        expr += ["#n = :n", "name_lc = :nlc"]
        names["#n"] = "name"
        vals[":n"] = name
        vals[":nlc"] = name.lower()
        artist["name"] = name
        artist["name_lc"] = name.lower()
    if biography:
        expr.append("biography = :b")
        vals[":b"] = biography
        artist["biography"] = biography

    if expr:
        content_table.update_item(
            Key={"PK": artist_id, "SK": "META"},
            UpdateExpression="SET " + ", ".join(expr),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=vals
        )

    if name:
        linked = query_all(content_table, KeyConditionExpression=Key("PK").eq(artist_id) & Key("SK").begins_with("CONTENT~"))
        with content_table.batch_writer() as batch:
            for i in linked:
                if "artists" in i:
                    i["artists"] = [{**a, "name": name} if a["artist_id"] == artist_id else a for a in i["artists"]]
                    batch.put_item(Item=i)

    if genres is not None:
        old = artist.get("genres", [])
        with content_table.batch_writer() as batch:
            for g in old:
                batch.delete_item(Key={"PK": g["genre_id"], "SK": f"CONTENT~{artist_id}"})
            for g in genres:
                batch.put_item(Item={**artist, "PK": g["genre_id"], "SK": f"CONTENT~{artist_id}"})
        artist["genres"] = genres
        content_table.put_item(Item=artist)
    return artist


def update_album(album_id, name=None, genres=None, artists=None):
    album = content_table.get_item(Key={"PK": album_id, "SK": "META"}).get("Item")
    if not album:
        return None

    expr, names, vals = [], {}, {}
    if name:
        expr += ["#n = :n", "name_lc = :nlc"]
        names["#n"] = "name"
        vals[":n"] = name
        vals[":nlc"] = name.lower()
        album["name"] = name
        album["name_lc"] = name.lower()

    if expr:
        content_table.update_item(
            Key={"PK": album_id, "SK": "META"},
            UpdateExpression="SET " + ", ".join(expr),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=vals
        )

    with content_table.batch_writer() as batch:
        if genres is not None:
            for g in album.get("genres", []):
                batch.delete_item(Key={"PK": g["genre_id"], "SK": f"CONTENT~{album_id}"})
            for g in genres:
                batch.put_item(Item={**album, "PK": g["genre_id"], "SK": f"CONTENT~{album_id}"})
            album["genres"] = genres
        if artists is not None:
            for a in album.get("artists", []):
                batch.delete_item(Key={"PK": a["artist_id"], "SK": f"CONTENT~{album_id}"})
            for a in artists:
                batch.put_item(Item={**album, "PK": a["artist_id"], "SK": f"CONTENT~{album_id}"})
            album["artists"] = artists
        batch.put_item(Item=album)
    return album


def update_single(single_id, name=None, genres=None, artists=None):
    single = content_table.get_item(Key={"PK": single_id, "SK": "META"}).get("Item")
    if not single:
        return None

    expr, names, vals = [], {}, {}
    if name:
        expr += ["#n = :n", "name_lc = :nlc"]
        names["#n"] = "name"
        vals[":n"] = name
        vals[":nlc"] = name.lower()
        single["name"] = name
        single["name_lc"] = name.lower()

    if expr:
        content_table.update_item(
            Key={"PK": single_id, "SK": "META"},
            UpdateExpression="SET " + ", ".join(expr),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=vals
        )

    with content_table.batch_writer() as batch:
        if genres is not None:
            for g in single.get("genres", []):
                batch.delete_item(Key={"PK": g["genre_id"], "SK": f"CONTENT~{single_id}"})
            for g in genres:
                batch.put_item(Item={**single, "PK": g["genre_id"], "SK": f"CONTENT~{single_id}"})
            single["genres"] = genres
        if artists is not None:
            for a in single.get("artists", []):
                batch.delete_item(Key={"PK": a["artist_id"], "SK": f"CONTENT~{single_id}"})
            for a in artists:
                batch.put_item(Item={**single, "PK": a["artist_id"], "SK": f"CONTENT~{single_id}"})
            single["artists"] = artists
        batch.put_item(Item=single)
    return single


def update_song(album_or_single_id, pos, song_id, name=None, genres=None, artists=None):
    key = {"PK": album_or_single_id, "SK": f"POS~{pos}~{song_id}"}
    song = content_table.get_item(Key=key).get("Item")
    if not song:
        return None

    expr, names, vals = [], {}, {}
    if name:
        expr += ["#n = :n", "name_lc = :nlc"]
        names["#n"] = "name"
        vals[":n"] = name
        vals[":nlc"] = name.lower()
        song["name"] = name
        song["name_lc"] = name.lower()

    if expr:
        content_table.update_item(
            Key=key,
            UpdateExpression="SET " + ", ".join(expr),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=vals
        )

    with content_table.batch_writer() as batch:
        if genres is not None:
            for g in song.get("genres", []):
                batch.delete_item(Key={"PK": g["genre_id"], "SK": f"CONTENT~{song_id}"})
            for g in genres:
                batch.put_item(Item={**song, "PK": g["genre_id"], "SK": f"CONTENT~{song_id}"})
            song["genres"] = genres
        if artists is not None:
            for a in song.get("artists", []):
                batch.delete_item(Key={"PK": a["artist_id"], "SK": f"CONTENT~{song_id}"})
            for a in artists:
                batch.put_item(Item={**song, "PK": a["artist_id"], "SK": f"CONTENT~{song_id}"})
            song["artists"] = artists
        batch.put_item(Item=song)
    return song


def update_user(user_id, updates: dict):
    expr, names, vals = [], {}, {}
    for k, v in updates.items():
        names[f"#{k}"] = k
        vals[f":{k}"] = v
        expr.append(f"#{k} = :{k}")
    if not expr:
        return
    userdata_table.update_item(
        Key={"user_id": user_id, "SK": "META"},
        UpdateExpression="SET " + ", ".join(expr),
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=vals
    )


def update_playlist(user_id, playlist_id, name):
    userdata_table.update_item(
        Key={"user_id": user_id, "SK": f"{playlist_id}~CONTENT"},
        UpdateExpression="SET #n = :n",
        ExpressionAttributeNames={"#n": "name"},
        ExpressionAttributeValues={":n": name}
    )


def update_rating(user_id, song_id, rating):
    userdata_table.update_item(
        Key={"user_id": user_id, "SK": f"RATING~{song_id}"},
        UpdateExpression="SET rating = :r, rating_user = :ru",
        ExpressionAttributeValues={
            ":r": str(rating),
            ":ru": f"{str(rating)}~{user_id}"
        }
    )
