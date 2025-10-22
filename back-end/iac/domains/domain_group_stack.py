from iac.domains.users.subscriptions_stack import SubscriptionsStack
from iac.domains.users.interactions_stack import InteractionsStack
from iac.shared.shared_resources_stack import SharedResourcesStack
from iac.domains.users.playlists_stack import PlaylistsStack
from iac.domains.misc.email_test_stack import EmailTestStack
from iac.domains.content.artists_stack import ArtistsStack
from iac.domains.content.singles_stack import SinglesStack
from iac.domains.content.albums_stack import AlbumsStack
from iac.domains.content.genres_stack import GenresStack
from iac.domains.users.ratings_stack import RatingsStack
from iac.domains.users.auth_stack import AuthStack
from iac.api_gateway_stack import ApiGatewayStack
from constructs import Construct
from aws_cdk import NestedStack


class DomainGroupStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, shared: SharedResourcesStack, api_gateway: ApiGatewayStack, **kwargs):
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
            shared.email_stack,
            env_vars
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
            env_vars
        )

        AlbumsStack(
            self, "AlbumsStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars
        )

        ArtistsStack(
            self, "ArtistsStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars
        )

        GenresStack(
            self, "GenresStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars
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
            env_vars
        )

        SinglesStack(
            self, "SinglesStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars
        )

        RatingsStack(
            self, "RatingsStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            env_vars
        )

        SubscriptionsStack(
            self, "SubscriptionsStack",
            shared.dynamo_db_stack,
            shared.s3_stack,
            shared.libs_layer_stack,
            shared.auth_layer_stack,
            shared.utils_layer_stack,
            api_gateway,
            shared.email_stack,
            env_vars
        )
