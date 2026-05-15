import json
import os

import boto3

from config import AWS_CONFIGS, TABLES


SNAPSHOT_DIR = "snapshots"


def convert_dynamodb_item(item):

    cleaned = {}

    for key, value in item.items():

        if "S" in value:
            cleaned[key] = value["S"]

        elif "N" in value:
            cleaned[key] = value["N"]

        else:
            cleaned[key] = str(value)

    return cleaned


def save_snapshot(environments):

    if not os.path.exists(SNAPSHOT_DIR):
        os.makedirs(SNAPSHOT_DIR)

    final_result = {}

    for env in environments:

        config = AWS_CONFIGS[env]

        dynamodb = boto3.client(
            "dynamodb",
            aws_access_key_id=config["aws_access_key_id"],
            aws_secret_access_key=config["aws_secret_access_key"],
            region_name=config["region"]
        )

        env_data = {}

        for table in TABLES:

            response = dynamodb.scan(
                TableName=table
            )

            items = response.get("Items", [])

            cleaned_items = []

            for item in items:

                cleaned_item = convert_dynamodb_item(item)

                cleaned_items.append(cleaned_item)

            env_data[table] = cleaned_items

            print(
                f"{env} | {table} | Records: {len(cleaned_items)}"
            )

        snapshot_path = os.path.join(
            SNAPSHOT_DIR,
            f"{env.lower()}_snapshot.json"
        )

        with open(snapshot_path, "w") as f:

            json.dump(
                env_data,
                f,
                indent=4
            )

        final_result[env] = env_data

        print(
            f"Snapshot saved: {snapshot_path}"
        )

    return final_result
