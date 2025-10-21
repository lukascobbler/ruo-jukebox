from boto3.dynamodb.conditions import Key
import boto3, uuid

genres = ["Rock", "Pop", "Jazz", "Blues", "Classical", "Electronic", "Hip-Hop", "Metal", "Latin", "Soul", "Country", "Reggae"]

def query_all(table, **kwargs):
    items = []
    resp = table.query(**kwargs)
    items.extend(resp["Items"])
    while "LastEvaluatedKey" in resp:
        resp = table.query(ExclusiveStartKey=resp["LastEvaluatedKey"], **kwargs)
        items.extend(resp["Items"])
    return items

def delete_all_genres(table):
    items = query_all(table, IndexName="byType", KeyConditionExpression=Key("content_type").eq("GENRE"))
    with table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})

def create_genre(table, name):
    genre_id = f"GENRE~{uuid.uuid4()}"
    item = {
        "PK": genre_id,
        "SK": "META",
        "genre_id": genre_id,
        "content_type": "GENRE",
        "name": name
    }
    table.put_item(Item=item)
    return item

def reset_genres():
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ContentTable")
    delete_all_genres(table)
    for g in genres:
        create_genre(table, g)
    print("Genres reset complete.")

if __name__ == "__main__":
    reset_genres()
