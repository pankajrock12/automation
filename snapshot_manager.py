import boto3
import json
import os

from config import TABLES, AWS_CONFIGS

SNAPSHOT_DIR = "snapshots"

os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def scan_table(table_name, aws_config):

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=aws_config["region"],
        aws_access_key_id=aws_config["access_key"],
        aws_secret_access_key=aws_config["secret_key"]
    )

    table = dynamodb.Table(table_name)

    response = table.scan()

    items = response.get("Items", [])

    return items


def save_snapshot(env):

    try:

        snapshot_data = {}

        summary = []

        aws_config = AWS_CONFIGS[env]

        for table_name in TABLES[env]:

            items = scan_table(table_name, aws_config)

            snapshot_data[table_name] = items

            summary.append({
                "table": table_name,
                "records": len(items)
            })

        file_path = os.path.join(
            SNAPSHOT_DIR,
            f"{env.lower()}_snapshot.json"
        )

        with open(file_path, "w") as f:
            json.dump(snapshot_data, f, indent=4)

        return {
            "success": True,
            "env": env,
            "summary": summary
        }

    except Exception as e:

        return {
            "success": False,
            "env": env,
            "error": str(e)
        }
