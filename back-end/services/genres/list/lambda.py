from pre_authorize import pre_authorize
from general_utils import response
from read import get, list_genres


@pre_authorize(["Admin", "User"])
def lambda_handler(event, context):
    all_genres = list_genres()

    # todo add subscriptions

    return response(200, all_genres)