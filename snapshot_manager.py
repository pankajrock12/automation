import os
import json
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from config import AWS_CONFIGS, TABLES


SNAPSHOT_DIR = "snapshots"

os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def get_dynamodb_client(env_name):

    env = AWS_CONFIGS[env_name]

    session = boto3.Session(
        aws_access_key_id=env["aws_access_key_id"],
        aws_secret_access_key=env["aws_secret_access_key"],
        aws_session_token=env.get("aws_session_token"),
        region_name=env["region"]
    )

    client = session.client(
        "dynamodb",
        verify=False,
        config=Config(
            retries={"max_attempts": 3},
            connect_timeout=60,
            read_timeout=60
        )
    )

    return client


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


def save_snapshot(env_name):

    try:

        print(f"\n========== {env_name} SNAPSHOT START ==========")

        client = get_dynamodb_client(env_name)

        snapshot_data = {}

        summary = []

        for table_name in TABLES:

            try:

                print(f"\nScanning table: {table_name}")

                items = scan_table(client, table_name)

                print(f"Items found: {len(items)}")

                if len(items) > 0:
                    print("First item sample:")
                    print(items[0])

                snapshot_data[table_name] = items

                summary.append({
                    "table": table_name,
                    "records": len(items)
                })

            except Exception as table_error:

                print(f"Error scanning table {table_name}")
                print(str(table_error))

                snapshot_data[table_name] = []

                summary.append({
                    "table": table_name,
                    "records": 0,
                    "error": str(table_error)
                })

        file_path = os.path.join(
            SNAPSHOT_DIR,
            f"{env_name.lower()}_snapshot.json"
        )

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, indent=4)

        print(f"\nSnapshot saved: {file_path}")

        print(f"========== {env_name} SNAPSHOT COMPLETE ==========\n")

        return {
            "success": True,
            "env": env_name,
            "summary": summary,
            "file": file_path
        }

    except ClientError as e:

        print("AWS Client Error")
        print(str(e))

        return {
            "success": False,
            "env": env_name,
            "error": str(e)
        }

    except Exception as e:

        print("General Error")
        print(str(e))

        return {
            "success": False,
            "env": env_name,
            "error": str(e)
        }
