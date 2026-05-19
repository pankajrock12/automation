import json

from report_generator import generate_html_report


def load_snapshot(env):

    with open(
        f"snapshots/{env}.json",
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def compare_two_env(base_env, compare_env):

    base_data = load_snapshot(base_env)

    compare_data = load_snapshot(compare_env)

    base_structure = base_data["structure"]

    compare_structure = compare_data["structure"]

    base_keys = set(str(base_structure))
    compare_keys = set(str(compare_structure))

    matched = len(base_keys.intersection(compare_keys))

    different = len(base_keys.symmetric_difference(compare_keys))

    missing = max(
        0,
        len(base_keys - compare_keys)
    )

    details = []

    if different > 0:

        details.append({
            "lookupCode": "STRUCTURE_MISMATCH",
            "status": "Different",
            "table": compare_data["table"]
        })

    return {
        "base_env": base_env,
        "compare_env": compare_env,
        "matched": matched,
        "different": different,
        "missing": missing,
        "details": details
    }


def compare_snapshots():

    results = []

    results.append(
        compare_two_env("DEV", "TEST")
    )

    results.append(
        compare_two_env("DEV", "MO")
    )

    results.append(
        compare_two_env("DEV", "PROD")
    )

    report_path = generate_html_report(results)

    return report_path
