AWS_CONFIGS = {

    "DEV": {
        "aws_access_key_id": "YOUR_DEV_ACCESS_KEY",
        "aws_secret_access_key": "YOUR_DEV_SECRET_KEY",
        "aws_session_token": "YOUR_DEV_SESSION_TOKEN",
        "region": "us-east-1"
    },

    "TEST": {
        "aws_access_key_id": "YOUR_TEST_ACCESS_KEY",
        "aws_secret_access_key": "YOUR_TEST_SECRET_KEY",
        "aws_session_token": "YOUR_TEST_SESSION_TOKEN",
        "region": "us-east-1"
    },

    "MO": {
        "aws_access_key_id": "YOUR_MO_ACCESS_KEY",
        "aws_secret_access_key": "YOUR_MO_SECRET_KEY",
        "aws_session_token": "YOUR_MO_SESSION_TOKEN",
        "region": "us-east-1"
    },

    "PROD": {
        "aws_access_key_id": "YOUR_PROD_ACCESS_KEY",
        "aws_secret_access_key": "YOUR_PROD_SECRET_KEY",
        "aws_session_token": "YOUR_PROD_SESSION_TOKEN",
        "region": "us-east-1"
    }
}


TABLES = [
    "pabio-bill-lookup-table-dev",
    "pabio-bill-lookup-table-test",
    "pabio-bill-lookup-table-mo",
    "pabio-bill-lookup-table-prod"
]
