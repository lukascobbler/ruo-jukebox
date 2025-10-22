from pre_authorize import pre_authorize
import os, json, time, boto3


@pre_authorize(['Admin'])
def lambda_handler(event, context):
    ...
