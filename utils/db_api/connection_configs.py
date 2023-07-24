import os


class ConnectionConfig:
    @classmethod
    def get_postgres_connection_config(cls):
        db_name = os.environ.get("PROD_DATABASE")
        db_user = os.environ.get("PROD_USER")
        db_password = os.environ.get("PROD_PASSWORD")
        db_host = os.environ.get("PROD_HOST")
        db_port = os.environ.get("PROD_PORT")

        postgres_connection_config = {
            "dbname": db_name,
            "password": db_password,
            "user": db_user,
            "port": db_port,
            "host": db_host
        }

        return postgres_connection_config

    @classmethod
    def get_test_db_connection_config(cls):
        db_name = os.environ.get("TEST_DATABASE")
        db_user = os.environ.get("TEST_USER")
        db_password = os.environ.get("TEST_PASSWORD")
        db_host = os.environ.get("TEST_HOST")
        db_port = os.environ.get("TEST_PORT")

        postgres_connection_config = {
            "dbname": db_name,
            "password": db_password,
            "user": db_user,
            "port": db_port,
            "host": db_host
        }

        return postgres_connection_config
