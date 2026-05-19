import boto3
import json
import os

from config import TABLES


def create_client(credentials):

    return boto3.client(
        "dynamodb",
        region_name=credentials["region"],
        aws_access_key_id=credentials["aws_access_key_id"],
        aws_secret_access_key=credentials["aws_secret_access_key"],
        aws_session_token=credentials["aws_session_token"],
        verify=False
    )


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


def save_snapshot(
    environments,
    credentials_map
):

    os.makedirs("snapshots", exist_ok=True)

    for env in environments:

        try:

            print(f"\nProcessing {env}")

            table = TABLES[env]

            credentials = credentials_map[env]

            dynamodb = create_client(credentials)

            # FIRST SCAN
            response = dynamodb.scan(
                TableName=table
            )

            items = response.get("Items", [])

            # PAGINATION
            while "LastEvaluatedKey" in response:

                response = dynamodb.scan(
                    TableName=table,
                    ExclusiveStartKey=response["LastEvaluatedKey"]
                )

                items.extend(
                    response.get("Items", [])
                )

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

            print(f"{env} snapshot saved")

        except Exception as e:

            print(f"\nERROR in {env}")
            print(str(e))

            return f"Failed while processing {env}: {str(e)}"

    return "Snapshots captured successfully"
