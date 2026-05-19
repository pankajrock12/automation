import boto3
import json
import os
import urllib3

from botocore.config import Config
from config import TABLES

urllib3.disable_warnings()


def create_client():

    session = boto3.Session()

    dynamodb = session.client(
        "dynamodb",
        region_name="us-east-1",
        verify=False,
        config=Config(
            retries={
                "max_attempts": 3,
                "mode": "standard"
            }
        )
    )

    return dynamodb


def extract_structure(data):

    if isinstance(data, dict):

        structure = {}

        for key, value in data.items():

            if key in [
                "S",
                "N",
                "BOOL",
                "M",
                "L",
                "NULL"
            ]:

                structure["datatype"] = key

                if isinstance(value, dict):

                    structure["children"] = extract_structure(value)

                elif isinstance(value, list):

                    child_list = []

                    for item in value:

                        child_list.append(
                            extract_structure(item)
                        )

                    structure["children"] = child_list

            else:

                structure[key] = extract_structure(value)

        return structure

    elif isinstance(data, list):

        return [
            extract_structure(item)
            for item in data
        ]

    else:

        return str(type(data).__name__)


def save_snapshot(environments):

    os.makedirs("snapshots", exist_ok=True)

    dynamodb = create_client()

    for env in environments:

        try:

            print(f"\nProcessing {env}")

            table = TABLES[env]

            print(f"TABLE = {table}")

            response = dynamodb.scan(
                TableName=table,
                Limit=10
            )

            items = response.get("Items", [])

            structure = extract_structure(items)

            output = {
                "environment": env,
                "table": table,
                "item_count": len(items),
                "structure": structure
            }

            with open(
                f"snapshots/{env}.json",
                "w"
            ) as file:

                json.dump(
                    output,
                    file,
                    indent=4
                )

            print(f"{env} snapshot saved successfully")

        except Exception as e:

            print(f"\nERROR in {env}")
            print(str(e))

            raise Exception(
                f"Failed while processing {env}: {str(e)}"
            )
