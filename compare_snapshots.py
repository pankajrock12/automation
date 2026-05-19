import boto3
import json
import time
import urllib3

from config import REGION
from report_generator import generate_html_report

# ======================================================
# DISABLE SSL WARNINGS
# ======================================================

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

# ======================================================
# DYNAMODB CLIENT
# ======================================================

client = boto3.client(
    "dynamodb",
    region_name=REGION,
    verify=False
)

print(f"CONNECTED REGION = {client.meta.region_name}")

# ======================================================
# GET TABLE SCHEMA
# ======================================================

def get_table_schema(table_name):

    table_name = table_name.strip()

    print(f"\nDESCRIBING TABLE : {repr(table_name)}")

    response = client.describe_table(
        TableName=table_name
    )

    return response["Table"]

# ======================================================
# GET TABLE ITEMS
# ======================================================

def get_table_items(table_name):

    table_name = table_name.strip()

    print(f"\nSCANNING TABLE : {repr(table_name)}")

    items = []

    paginator = client.get_paginator("scan")

    try:

        for page in paginator.paginate(
            TableName=table_name,
            PaginationConfig={
                "PageSize": 100
            }
        ):

            page_items = page.get("Items", [])

            items.extend(page_items)

            print(f"Loaded Items : {len(items)}")

            time.sleep(0.2)

            # SAFETY LIMIT
            if len(items) >= 1000:
                break

    except Exception as e:

        print(f"\nSCAN ERROR : {str(e)}")

        return []

    print(f"\nTOTAL ITEMS : {len(items)}")

    return items

# ======================================================
# PRINT TABLE SCHEMA
# ======================================================

def print_schema_details(name, schema):

    print("\n====================================")
    print(f"{name.upper()} TABLE SCHEMA")
    print("====================================")

    print("\nTable Name:")
    print(schema["TableName"])

    print("\nPartition / Sort Keys:")
    print(schema["KeySchema"])

    print("\nAttribute Definitions:")
    print(schema["AttributeDefinitions"])

    print("\nItem Count:")
    print(schema["ItemCount"])

    print("\nTable Status:")
    print(schema["TableStatus"])

# ======================================================
# SCHEMA COMPARISON
# ======================================================

def compare_schema(schema1, schema2, env1, env2):

    print("\n====================================")
    print(f"SCHEMA COMPARISON {env1} VS {env2}")
    print("====================================")

    matched = 0
    different = 0

    attributes = [
        "KeySchema",
        "AttributeDefinitions",
        "TableStatus"
    ]

    for attr in attributes:

        print("\n------------------------------------")
        print(f"Checking : {attr}")
        print("------------------------------------")

        if schema1[attr] == schema2[attr]:

            matched += 1

            print("STATUS MATCHED")

        else:

            different += 1

            print("STATUS : DIFFERENT")

            print(f"\n{env1} VALUE:")
            print(schema1[attr])

            print(f"\n{env2} VALUE:")
            print(schema2[attr])

    print("\n====================================")
    print("SCHEMA SUMMARY")
    print("====================================")

    print(f"Matched Attributes : {matched}")
    print(f"Different Attributes : {different}")

# ======================================================
# EXTRACT ONLY STRUCTURE
# ======================================================

def extract_structure(data):

    if isinstance(data, dict):

        structure = {}

        for key, value in data.items():

            if key in [
                "S",
                "N",
                "BOOL",
                "NULL",
                "M",
                "L"
            ]:

                if key == "M":

                    structure["M"] = extract_structure(value)

                elif key == "L":

                    if len(value) > 0:

                        structure["L"] = extract_structure(
                            value[0]
                        )

                    else:

                        structure["L"] = []

                else:

                    structure[key] = "DATATYPE"

            else:

                structure[key] = extract_structure(value)

        return structure

    elif isinstance(data, list):

        if len(data) > 0:

            return [
                extract_structure(data[0])
            ]

        else:

            return []

    else:

        return type(data).__name__

# ======================================================
# STRUCTURE COMPARISON
# ======================================================

def compare_table_structure(items1, items2, env1, env2):

    print("\n\n############################################")
    print(f"STRUCTURE COMPARISON : {env1} vs {env2}")
    print("############################################")

    if not items1:
        print(f"\nNo items found in {env1}")

    if not items2:
        print(f"\nNo items found in {env2}")

    map1 = {}
    map2 = {}

    report_rows = []

    # ==================================================
    # CREATE MAP FOR ENV1
    # ==================================================

    for item in items1:

        lookup_code = item.get(
            "lookupCode",
            {}
        ).get("S")

        if not lookup_code:
            continue

        map1[lookup_code] = item

    # ==================================================
    # CREATE MAP FOR ENV2
    # ==================================================

    for item in items2:

        lookup_code = item.get(
            "lookupCode",
            {}
        ).get("S")

        if not lookup_code:
            continue

        map2[lookup_code] = item

    # ==================================================
    # GET ALL UNIQUE LOOKUPCODES
    # ==================================================

    all_keys = sorted(
        set(map1.keys()).union(set(map2.keys()))
    )

    matched_count = 0
    different_count = 0
    missing_count = 0

    sequence = 1

    # ==================================================
    # LOOP THROUGH ALL LOOKUPCODES
    # ==================================================

    for key in all_keys:

        print("\n========================================")
        print(f"{sequence}. lookupCode : {key}")
        print("========================================")

        # ==============================================
        # MISSING IN ENV1
        # ==============================================

        if key not in map1:

            missing_count += 1

            status = f"Missing in {env1}"

            print(f"STATUS : {status}")

            report_rows.append({
                "sequence": sequence,
                "lookupCode": key,
                "status": status,
                "env1": "MISSING",
                "env2": "AVAILABLE"
            })

        # ==============================================
        # MISSING IN ENV2
        # ==============================================

        elif key not in map2:

            missing_count += 1

            status = f"Missing in {env2}"

            print(f"STATUS : {status}")

            report_rows.append({
                "sequence": sequence,
                "lookupCode": key,
                "status": status,
                "env1": "AVAILABLE",
                "env2": "MISSING"
            })

        # ==============================================
        # COMPARE STRUCTURE
        # ==============================================

        else:

            item1 = map1[key]
            item2 = map2[key]

            structure1 = extract_structure(item1)
            structure2 = extract_structure(item2)

            # FULL STRUCTURE MATCH

            if structure1 == structure2:

                matched_count += 1

                print("STATUS : MATCHED")

                report_rows.append({
                    "sequence": sequence,
                    "lookupCode": key,
                    "status": "MATCHED",
                    "env1": "MATCHED",
                    "env2": "MATCHED"
                })

            else:

                different_count += 1

                print("STATUS : DIFFERENT")

                print(f"\n{env1} STRUCTURE:")
                print(json.dumps(structure1, indent=2))

                print(f"\n{env2} STRUCTURE:")
                print(json.dumps(structure2, indent=2))

                report_rows.append({
                    "sequence": sequence,
                    "lookupCode": key,
                    "status": "DIFFERENT",
                    "env1": json.dumps(structure1),
                    "env2": json.dumps(structure2)
                })

        sequence += 1

    # ==================================================
    # FINAL SUMMARY
    # ==================================================

    print("\n############################################")
    print(f"FINAL SUMMARY : {env1} vs {env2}")
    print("############################################")

    print(f"Total LookupCodes Compared : {len(all_keys)}")
    print(f"Matched Items              : {matched_count}")
    print(f"Different Items            : {different_count}")
    print(f"Missing Items              : {missing_count}")

    report_name = f"{env1}_vs_{env2}_structure_report.html"

    generate_html_report(
        report_rows,
        report_name,
        env1,
        env2
    )

    print(f"\nHTML REPORT GENERATED : {report_name}")

    print("\nComparison Completed Successfully")
