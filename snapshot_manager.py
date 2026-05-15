import boto3
import json
import os

from config import ENVIRONMENTS

SNAPSHOT_FOLDER = "snapshots"

os.makedirs(SNAPSHOT_FOLDER, exist_ok=True)


def create_client(credentials):

    return boto3.client(
        "dynamodb",
        region_name=credentials["region"],
        aws_access_key_id=credentials["aws_access_key_id"],
        aws_secret_access_key=credentials["aws_secret_access_key"],
        aws_session_token=credentials["aws_session_token"],
        verify=False
    )


def scan_table(client, table_name):

    all_items = []

    response = client.scan(TableName=table_name)

    all_items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:

        response = client.scan(
            TableName=table_name,
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )

        all_items.extend(response.get("Items", []))

    return all_items


def save_snapshot(environment):

    env_config = ENVIRONMENTS[environment]

    credentials = env_config["credentials"]
    tables = env_config["tables"]

    client = create_client(credentials)

    snapshot_data = {}

    for table in tables:

        try:

            items = scan_table(client, table)

            snapshot_data[table] = items

            print(f"{environment} -> {table} -> {len(items)} items captured")

        except Exception as e:

            print(f"ERROR in {environment} {table}")

            print(str(e))

            snapshot_data[table] = []

    output_file = f"{SNAPSHOT_FOLDER}/{environment}.json"

    with open(output_file, "w") as file:

        json.dump(snapshot_data, file, indent=4)

    return snapshot_data
