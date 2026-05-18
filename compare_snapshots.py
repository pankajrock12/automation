import json
import os
import pandas as pd

SNAPSHOT_DIR = "snapshots"

ENVIRONMENTS = ["DEV", "TEST", "MO", "PROD"]


def load_snapshot(env):
    path = os.path.join(SNAPSHOT_DIR, f"{env}.json")

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_item_key(item):
    """
    Try common DynamoDB key names automatically
    """

    possible_keys = [
        "id",
        "ID",
        "pk",
        "PK",
        "policyNumber",
        "billNumber",
        "lookupId",
        "key"
    ]

    for k in possible_keys:
        if k in item:
            return str(item[k])

    return str(hash(json.dumps(item, sort_keys=True)))


def compare_snapshots():

    env_data = {}

    for env in ENVIRONMENTS:
        items = load_snapshot(env)

        env_data[env] = {
            get_item_key(item): item
            for item in items
        }

    all_keys = set()

    for env in ENVIRONMENTS:
        all_keys.update(env_data[env].keys())

    rows = []

    for key in all_keys:

        row = {
            "Key": key
        }

        values = []

        for env in ENVIRONMENTS:

            value = env_data[env].get(key)

            if value:
                row[env] = "Present"
                values.append(json.dumps(value, sort_keys=True))
            else:
                row[env] = "Missing"

        row["Status"] = (
            "MATCH"
            if len(set(values)) == 1 and len(values) == len(ENVIRONMENTS)
            else "DIFFERENT"
        )

        rows.append(row)

    df = pd.DataFrame(rows)

    return df
