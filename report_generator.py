import os


def generate_html_report(results):

    os.makedirs("reports", exist_ok=True)

    report_path = "reports/final_validation_report.html"

    html = """
    <html>
    <head>
        <title>DynamoDB Validation Report</title>

        <style>

            body{
                font-family: Arial;
                padding:20px;
            }

            h1{
                color:#1f4e78;
            }

            h2{
                margin-top:40px;
                color:#2f5597;
            }

            h3{
                margin-top:30px;
            }

            table{
                width:100%;
                border-collapse:collapse;
                margin-top:10px;
                margin-bottom:30px;
            }

            th{
                background-color:#1f1f1f;
                color:white;
                padding:10px;
                border:1px solid #d9d9d9;
            }

            td{
                padding:8px;
                border:1px solid #d9d9d9;
            }

            .matched{
                background-color:#d9ead3;
            }

            .different{
                background-color:#f4cccc;
            }

            .missing{
                background-color:#fff2cc;
            }

            .summary-card{
                width:30%;
                display:inline-block;
                margin-right:10px;
                padding:20px;
                color:white;
                font-size:20px;
                font-weight:bold;
                border-radius:8px;
            }

            .green{
                background-color:#2e7d32;
            }

            .red{
                background-color:#c62828;
            }

            .orange{
                background-color:#ef6c00;
            }

        </style>

    </head>

    <body>

    <h1>DynamoDB Environment Validation Report</h1>
    """

    total_matched = 0
    total_different = 0
    total_missing = 0

    for result in results:

        total_matched += result.get("matched", 0)
        total_different += result.get("different", 0)
        total_missing += result.get("missing", 0)

    html += f"""

    <h2>Summary</h2>

    <div class="summary-card green">
        Matched<br><br>
        {total_matched}
    </div>

    <div class="summary-card red">
        Different<br><br>
        {total_different}
    </div>

    <div class="summary-card orange">
        Missing<br><br>
        {total_missing}
    </div>

    """

    for result in results:

        html += f"""

        <h2>
            {result.get("baseEnv", "")}
            vs
            {result.get("compareEnv", "")}
        </h2>

        <table>

            <tr>
                <th>Matched</th>
                <th>Different</th>
                <th>Missing</th>
            </tr>

            <tr>
                <td class="matched">
                    {result.get("matched", 0)}
                </td>

                <td class="different">
                    {result.get("different", 0)}
                </td>

                <td class="missing">
                    {result.get("missing", 0)}
                </td>
            </tr>

        </table>

        """

        html += """

        <table>

            <tr>
                <th>Table</th>
                <th>LookupCode</th>
                <th>Field</th>
                <th>Base Datatype</th>
                <th>Compare Datatype</th>
                <th>Status</th>
            </tr>

        """

        for detail in result.get("details", []):

            status = detail.get("status", "")

            css_class = ""

            if status == "MATCHED":
                css_class = "matched"

            elif status == "DIFFERENT":
                css_class = "different"

            else:
                css_class = "missing"

            html += f"""

            <tr class="{css_class}">

                <td>
                    {detail.get("table", "UNKNOWN_TABLE")}
                </td>

                <td>
                    {detail.get("lookupCode", "UNKNOWN_LOOKUP")}
                </td>

                <td>
                    {detail.get("field", "")}
                </td>

                <td>
                    {detail.get("baseDatatype", "")}
                </td>

                <td>
                    {detail.get("compareDatatype", "")}
                </td>

                <td>
                    {detail.get("status", "")}
                </td>

            </tr>

            """

        html += "</table>"

    html += """

    </body>
    </html>

    """

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(html)

    return report_path
