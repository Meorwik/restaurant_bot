class ConnectionConfig:
    @classmethod
    def get_postgres_connection_config(cls):
        db_name = ""
        db_user = ""
        db_password = ""
        db_host = ""
        db_port = ""

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
        db_name = ""
        db_user = ""
        db_password = ""
        db_host = ""
        db_port = ""

        postgres_connection_config = {
            "dbname": db_name,
            "password": db_password,
            "user": db_user,
            "port": db_port,
            "host": db_host
        }

        return postgres_connection_config
