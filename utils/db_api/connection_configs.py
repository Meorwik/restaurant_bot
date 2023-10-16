import os


class ConnectionConfig:
    @classmethod
    def get_test_db_connection_config(cls):
        postgres_connection_config = os.environ.get("TEST_DB")
        return postgres_connection_config
