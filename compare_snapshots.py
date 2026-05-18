import json
import os
from datetime import datetime


def load_snapshot(env):
    path = f"snapshots/{env.lower()}_snapshot.json"

    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def compare_snapshots():

    dev_data = load_snapshot("dev")
    test_data = load_snapshot("test")
    mo_data = load_snapshot("mo")
    prod_data = load_snapshot("prod")

    report_lines = []

    report_lines.append("""
    <html>
    <head>
        <title>DynamoDB Validation Report</title>
        <style>
            body {
                font-family: Arial;
                margin: 20px;
            }

            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
            }

            th, td {
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }

            th {
                background-color: #f2f2f2;
            }

            .missing {
                background-color: #ffcccc;
            }

            .matched {
                background-color: #ccffcc;
            }

            .different {
                background-color: #fff0b3;
            }
        </style>
    </head>
    <body>
    """)

    report_lines.append(
        f"<h1>DynamoDB Validation Report</h1>"
    )

    report_lines.append(
        f"<p>Generated: {datetime.now()}</p>"
    )

    all_keys = set()

    for dataset in [dev_data, test_data, mo_data, prod_data]:
        all_keys.update(dataset.keys())

    report_lines.append("""
    <table>
        <tr>
            <th>Key</th>
            <th>DEV</th>
            <th>TEST</th>
            <th>MO</th>
            <th>PROD</th>
            <th>Status</th>
        </tr>
    """)

    for key in sorted(all_keys):

        dev_value = str(dev_data.get(key, "MISSING"))
        test_value = str(test_data.get(key, "MISSING"))
        mo_value = str(mo_data.get(key, "MISSING"))
        prod_value = str(prod_data.get(key, "MISSING"))

        values = [dev_value, test_value, mo_value, prod_value]

        if all(v == values[0] for v in values):
            status = "MATCHED"
            css = "matched"

        elif "MISSING" in values:
            status = "MISSING"
            css = "missing"

        else:
            status = "DIFFERENT"
            css = "different"

        report_lines.append(f"""
        <tr class="{css}">
            <td>{key}</td>
            <td>{dev_value}</td>
            <td>{test_value}</td>
            <td>{mo_value}</td>
            <td>{prod_value}</td>
            <td>{status}</td>
        </tr>
        """)

    report_lines.append("""
    </table>
    </body>
    </html>
    """)

    os.makedirs("reports", exist_ok=True)

    report_path = "reports/final_validation_report.html"

    with open(report_path, "w", encoding="utf-8") as file:
        file.write("\n".join(report_lines))

    return report_path
