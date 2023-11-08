import os


def get_connection_config():
    postgres_connection_config = os.environ.get("TEST_DB")
    return postgres_connection_config
