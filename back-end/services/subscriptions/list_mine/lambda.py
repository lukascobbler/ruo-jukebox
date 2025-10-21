import os, json
import boto3
from pre_authorize import pre_authorize

@pre_authorize(['Admin','LoggedInUser'])
def lambda_handler(event, context):
 # TODO finish