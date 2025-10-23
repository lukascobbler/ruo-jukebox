from iac.domains.users.subscriptions_stack import SubscriptionsStack
from iac.domains.users.interactions_stack import InteractionsStack
from iac.shared.shared_resources_stack import SharedResourcesStack
from iac.domains.users.playlists_stack import PlaylistsStack
from iac.domains.misc.email_test_stack import EmailTestStack
from iac.domains.content.artists_stack import ArtistsStack
from iac.domains.content.singles_stack import SinglesStack
from iac.domains.content.albums_stack import AlbumsStack
from iac.domains.content.search_stack import SearchStack
from iac.domains.content.genres_stack import GenresStack
from iac.domains.users.ratings_stack import RatingsStack
from iac.shared.api_gateway_stack import ApiGatewayStack
from iac.domains.users.auth_stack import AuthStack
from constructs import Construct
from aws_cdk import NestedStack


class DomainGroupStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, shared: SharedResourcesStack, api_gateway: ApiGatewayStack, branch: str, **kwargs):
        super().__init__(scope, stack_id, **kwargs)
        env_vars = shared.env_vars

        EmailTestStack(
            self, "EmailTestStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars,
            branch
        )

        AuthStack(
            self, "AuthStack",
            shared.cognito_stack,
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars,
            branch
        )

        subs_stack = SubscriptionsStack(  # create before singles and albums to get the SQS queue
            self, "SubscriptionsStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars,
            branch
        )

        AlbumsStack(
            self, "AlbumsStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars,
            branch,
            notify_queue=subs_stack.new_content_queue
        )

        ArtistsStack(
            self, "ArtistsStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars,
            branch
        )

        GenresStack(
            self, "GenresStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars,
            branch
        )

        InteractionsStack(
            self, "InteractionsStack",
            shared.dynamo_db_stack,
            env_vars
        )

        PlaylistsStack(
            self, "PlaylistsStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars,
            branch
        )

        SinglesStack(
            self, "SinglesStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars,
            branch,
            notify_queue=subs_stack.new_content_queue
        )

        RatingsStack(
            self, "RatingsStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars,
            branch
        )

        SearchStack(
            self, "SearchStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars,
            branch
        )
