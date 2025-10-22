import boto3, uuid, os, argparse
from botocore.exceptions import ClientError
from passlib.hash import pbkdf2_sha256


def get_user_pool_id_by_name(name: str, region: str):
    client = boto3.client("cognito-idp", region_name=region)
    paginator = client.get_paginator("list_user_pools")
    for page in paginator.paginate(MaxResults=60):
        for pool in page["UserPools"]:
            if pool["Name"] == name:
                return pool["Id"]
    raise ValueError(f"No user pool found with name '{name}' in region {region}")


def delete_all_users(cognito, user_pool_id):
    paginator = cognito.get_paginator("list_users")
    deleted = 0
    for page in paginator.paginate(UserPoolId=user_pool_id):
        for user in page["Users"]:
            username = user["Username"]
            try:
                cognito.admin_delete_user(UserPoolId=user_pool_id, Username=username)
                deleted += 1
            except ClientError as e:
                print(f"Failed to delete {username}: {e.response['Error']['Message']}")
    print(f"Deleted {deleted} users from pool {user_pool_id}")


def seed_users(branch: str):
    aws_region = os.environ.get("AWS_REGION", "eu-central-1")
    suffix = f"-{branch}" if branch != "main" else ""

    user_pool_name = f"JukeboxUserPool{suffix}"
    userdata_table_name = os.environ.get("USERDATA_TABLE", f"UserdataTable{suffix}")

    print(f"Resolving User Pool ID for '{user_pool_name}'...")
    user_pool_id = get_user_pool_id_by_name(user_pool_name, aws_region)
    print(f"Resolved pool ID: {user_pool_id}")

    cognito = boto3.client("cognito-idp", region_name=aws_region)
    dynamodb = boto3.resource("dynamodb", region_name=aws_region)
    table = dynamodb.Table(userdata_table_name)

    print("Removing all existing users...")
    delete_all_users(cognito, user_pool_id)

    users = [
        {
            "username": "a",
            "email": "admin@example.com",
            "password": "123456",
            "name": "Admin",
            "surname": "User",
            "birthday": "1990-01-01",
            "group": "Admin"
        },
        {
            "username": "u",
            "email": "user@example.com",
            "password": "123456",
            "name": "Regular",
            "surname": "User",
            "birthday": "1995-05-05",
            "group": "User"
        }
    ]

    for u in users:
        user_id = f"USER~{uuid.uuid4()}"
        print(f"Creating {u['username']} ({u['group']}) → {user_id}")

        hashed_password = pbkdf2_sha256.hash(u["password"])

        try:
            cognito.admin_create_user(
                UserPoolId=user_pool_id,
                Username=u["username"],
                UserAttributes=[
                    {"Name": "email", "Value": u["email"]},
                    {"Name": "email_verified", "Value": "true"},
                    {"Name": "given_name", "Value": u["name"]},
                    {"Name": "family_name", "Value": u["surname"]},
                    {"Name": "birthdate", "Value": u["birthday"]},
                    {"Name": "custom:userId", "Value": user_id}
                ],
                MessageAction="SUPPRESS"
            )

            cognito.admin_set_user_password(
                UserPoolId=user_pool_id,
                Username=u["username"],
                Password=u["password"],
                Permanent=True
            )

            cognito.admin_add_user_to_group(
                UserPoolId=user_pool_id,
                Username=u["username"],
                GroupName=u["group"]
            )

            table.put_item(Item={
                "user_id": user_id,
                "SK": "META",
                "username": u["username"],
                "email": u["email"],
                "password": hashed_password,
                "name": u["name"],
                "surname": u["surname"],
                "birthday": u["birthday"],
                "group": u["group"]
            })

            print(f"Created {u['username']} in {u['group']} group")

        except ClientError as e:
            err = e.response["Error"]["Message"]
            print(f"Failed to create {u['username']}: {err}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Cognito users with branch-specific suffix.")
    parser.add_argument("--branch", default="main", help="Branch name (default: main)")
    args = parser.parse_args()

    seed_users(args.branch)
