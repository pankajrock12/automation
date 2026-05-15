import os


def generate_html_report(results):

    html = """
    <html>
    <head>
        <title>DynamoDB Validation Report</title>

        <style>

            body {
                font-family: Arial;
                padding: 20px;
            }

            h1 {
                color: #1f77b4;
            }

            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 40px;
            }

            th, td {
                border: 1px solid #ccc;
                padding: 10px;
                text-align: left;
            }

            th {
                background-color: #333;
                color: white;
            }

            .matched {
                color: green;
                font-weight: bold;
            }

            .different {
                color: orange;
                font-weight: bold;
            }

            .missing {
                color: red;
                font-weight: bold;
            }

        </style>

    </head>

    <body>

    <h1>DynamoDB Validation Report</h1>
    """

    total_matched = 0
    total_different = 0
    total_missing = 0

    for result in results:

        total_matched += result["matched"]
        total_different += result["different"]
        total_missing += result["missing"]

    html += f"""
    <h2>Summary</h2>

    <table>

        <tr>
            <th>Matched</th>
            <th>Different</th>
            <th>Missing</th>
        </tr>

        <tr>
            <td class='matched'>{total_matched}</td>
            <td class='different'>{total_different}</td>
            <td class='missing'>{total_missing}</td>
        </tr>

    </table>
    """

    for result in results:

        html += f"""
        <h2>
            {result['base_env']} vs {result['compare_env']}
        </h2>

        <table>

            <tr>
                <th>Matched</th>
                <th>Different</th>
                <th>Missing</th>
            </tr>

            <tr>
                <td class='matched'>{result['matched']}</td>
                <td class='different'>{result['different']}</td>
                <td class='missing'>{result['missing']}</td>
            </tr>

        </table>
        """

        if result["details"]:

            html += """
            <table>

                <tr>
                    <th>LookupCode</th>
                    <th>Status</th>
                    <th>Table</th>
                </tr>
            """

            for item in result["details"]:

                html += f"""
                <tr>
                    <td>{item['lookupCode']}</td>
                    <td>{item['status']}</td>
                    <td>{item['table']}</td>
                </tr>
                """

            html += "</table>"

        else:

            html += "<p>No differences found</p>"

    html += """
    </body>
    </html>
    """

    if not os.path.exists("reports"):
        os.makedirs("reports")

    report_path = "reports/validation_report.html"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    return report_path
