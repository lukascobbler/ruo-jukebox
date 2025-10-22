from pre_authorize import pre_authorize
from read import get, list_genres
from general_utils import response


@pre_authorize(["Admin", "User"])
def lambda_handler(event, context):
    all_genres = list_genres()

    # todo add subscriptions

    return response(200, all_genres)