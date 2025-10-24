from pre_authorize import pre_authorize
from general_utils import response
import json


def lambda_handler(event, context):
    return response(200, error="Success")
