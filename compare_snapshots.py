import json
import os

SNAPSHOT_DIR = "snapshots"


def load_snapshot(env):

    file_path = os.path.join(
        SNAPSHOT_DIR,
        f"{env.lower()}_snapshot.json"
    )

    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r") as f:
        return json.load(f)


def compare_table(base_items, compare_items):

    matched = 0
    different = 0
    missing = 0

    details = []

    compare_lookup = {}

    for item in compare_items:

        lookup_code = item.get("lookupCode")

        if lookup_code:
            compare_lookup[lookup_code] = item

    for base_item in base_items:

        lookup_code = base_item.get("lookupCode")

        compare_item = compare_lookup.get(lookup_code)

        if compare_item is None:

            missing += 1

            details.append({
                "lookupCode": lookup_code,
                "status": "MISSING"
            })

            continue

        base_json = json.dumps(base_item, sort_keys=True)
        compare_json = json.dumps(compare_item, sort_keys=True)

        if base_json == compare_json:

            matched += 1

        else:

            different += 1

            details.append({
                "lookupCode": lookup_code,
                "status": "DIFFERENT"
            })

    return {
        "matched": matched,
        "different": different,
        "missing": missing,
        "details": details
    }


def compare_two_env(base_env, compare_env):

    base_snapshot = load_snapshot(base_env)
    compare_snapshot = load_snapshot(compare_env)

    final_details = []

    total_matched = 0
    total_different = 0
    total_missing = 0

    for table_name, base_items in base_snapshot.items():

        compare_items = compare_snapshot.get(table_name, [])

        result = compare_table(base_items, compare_items)

        total_matched += result["matched"]
        total_different += result["different"]
        total_missing += result["missing"]

        for detail in result["details"]:

            detail["table"] = table_name

            final_details.append(detail)

    return {
        "base_env": base_env,
        "compare_env": compare_env,
        "matched": total_matched,
        "different": total_different,
        "missing": total_missing,
        "details": final_details
    }


def compare_all():

    final_result = []

    comparisons = [
        ("DEV", "TEST"),
        ("DEV", "MO"),
        ("DEV", "PROD")
    ]

    for comparison in comparisons:

        base_env = comparison[0]
        compare_env = comparison[1]

        result = compare_two_env(
            base_env,
            compare_env
        )

        final_result.append(result)

    return final_result
