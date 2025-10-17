from constructs import Construct
from aws_cdk.aws_apigateway import AuthorizationType
from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
)

from iac.api_gateway_stack import ApiGatewayStack
from iac.cognito_stack import CognitoStack
from iac.common import mk_lambda
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack

class SongsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 cognito: CognitoStack, dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)

        auth_kwargs = cognito.auth_kwargs
        authorizer = cognito.authorizer

        song_init = mk_lambda("SongInitUpload", "services/music_service/song/init_upload", env, dynamo_db, s3)
        song_done = mk_lambda("SongCompleteUpload", "services/music_service/song/complete_upload", env, dynamo_db, s3)
        song_list = mk_lambda("SongList", "services/music_service/song/list", env, dynamo_db, s3)
        song_get = mk_lambda("SongGet", "services/music_service/song/get", env, dynamo_db, s3)
        song_update = mk_lambda("SongUpdate", "services/music_service/song/update", env, dynamo_db, s3)
        song_delete = mk_lambda("SongDelete", "services/music_service/song/delete", env, dynamo_db, s3)
        song_cov_init = mk_lambda("SongCoverInit", "services/music_service/song/init_cover_upload", env, dynamo_db, s3)
        song_cov_done = mk_lambda("SongCoverDone", "services/music_service/song/complete_cover", env, dynamo_db, s3)
        
        song = api_gateway.api.root.add_resource("song")
        song_id = song.add_resource("{id}")

        song.add_resource("init-upload").add_method(
            "POST",     
            apigw.LambdaIntegration(song_init), 
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        song.add_resource("complete-upload").add_method(
            "POST", 
            apigw.LambdaIntegration(song_done), 
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        song.add_method(
            "GET", 
            apigw.LambdaIntegration(song_list), 
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        song.add_resource("init-cover-upload").add_method(
            "POST", 
            apigw.LambdaIntegration(song_cov_init), 
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        song.add_resource("complete-cover").add_method(
            "POST",    
            apigw.LambdaIntegration(song_cov_done), 
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )

        song_id.add_method(
            "GET",    
            apigw.LambdaIntegration(song_get),    
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        song_id.add_method(
            "PATCH",  
            apigw.LambdaIntegration(song_update), 
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        song_id.add_method(
            "DELETE", 
            apigw.LambdaIntegration(song_delete), 
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
