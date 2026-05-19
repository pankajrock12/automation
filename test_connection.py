import boto3

client = boto3.client(
    "dynamodb",
    region_name="us-east-1",
    aws_access_key_id="PASTE_ACCESS_KEY",
    aws_secret_access_key="PASTE_SECRET_KEY",
    aws_session_token="PASTE_SESSION_TOKEN",
    verify=False
)

response = client.list_tables()

print("\nAVAILABLE TABLES:\n")

for table in response["TableNames"]:
    print(table)
