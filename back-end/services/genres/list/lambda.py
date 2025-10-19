import os, json
from dataclasses import asdict
import boto3
from boto3.dynamodb.conditions import Key
from model.model import GenreItem
from dataclasses import dataclass


@dataclass
class GenreItem:
    id: str
    name: str
    isSubscribed: bool | None

TABLE_NAME = os.environ['GENRES_TABLE']
dynamodb = boto3.resource('dynamodb')
genres_table = dynamodb.Table(TABLE_NAME)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
}

def lambda_handler(event, context):
    response = genres_table.query(
        KeyConditionExpression=Key("PK").eq("genres")
    )
    items = response.get("Items", [])
    genres = [
        asdict(GenreItem(
            id=item.get("genre_id"),
            name=item.get("Name"),
            isSubscribed=None
        ))
        for item in items
    ]
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": genres}
