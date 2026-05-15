import json
import os

SNAPSHOT_DIR = "snapshots"


def load_snapshot(env):

    file_path = os.path.join(
        SNAPSHOT_DIR,
        f"{env.lower()}_snapshot.json"
    )

    if not os.path.exists(file_path):
        return []

    with open(file_path, "r") as f:
        data = json.load(f)

    all_items = []

    for table_name, items in data.items():

        if isinstance(items, list):

            for item in items:
                item["_table"] = table_name
                all_items.append(item)

    return all_items


def extract_lookup_code(item):

    lookup_code = item.get("lookupCode")

    if isinstance(lookup_code, dict):

        if "S" in lookup_code:
            return lookup_code["S"]

        return json.dumps(lookup_code)

    return str(lookup_code)


def compare_table(base_items, compare_items):

    matched = 0
    different = 0
    missing = 0

    details = []

    compare_lookup = {}

    for item in compare_items:

        lookup_code = extract_lookup_code(item)

        compare_lookup[str(lookup_code)] = item

    for base_item in base_items:

        lookup_code = extract_lookup_code(base_item)

        compare_item = compare_lookup.get(
            str(lookup_code)
        )

        if compare_item is None:

            missing += 1

            details.append({
                "lookupCode": lookup_code,
                "status": "MISSING",
                "table": base_item.get("_table")
            })

            continue

        base_json = json.dumps(
            base_item,
            sort_keys=True
        )

        compare_json = json.dumps(
            compare_item,
            sort_keys=True
        )

        if base_json == compare_json:

            matched += 1

        else:

            different += 1

            details.append({
                "lookupCode": lookup_code,
                "status": "DIFFERENT",
                "table": base_item.get("_table")
            })

    return {
        "matched": matched,
        "different": different,
        "missing": missing,
        "details": details
    }


def compare_two_env(base_env, compare_env):

    base_items = load_snapshot(base_env)

    compare_items = load_snapshot(compare_env)

    result = compare_table(
        base_items,
        compare_items
    )

    result["base_env"] = base_env
    result["compare_env"] = compare_env

    return result


def compare_all():

    comparisons = [
        ("DEV", "TEST"),
        ("TEST", "MO"),
        ("MO", "PROD"),
        ("DEV", "MO"),
        ("DEV", "PROD"),
        ("TEST", "PROD")
    ]

    final_result = []

    for base_env, compare_env in comparisons:

        result = compare_two_env(
            base_env,
            compare_env
        )

        final_result.append(result)

    return final_result
