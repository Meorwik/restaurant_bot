import asyncpg


class DataBaseManager:
    def __init__(self, config):
        self.config = config
        self._connection = None

    async def set_connection(self):
        if self._connection is not None:
            self._connection = asyncpg.connect(
                f"""
                    dbname={self.config['dbname']}
                    user={self.config['user']}
                    password={self.config['password']}
                    host={self.config['host']}
                    port={self.config['port']}
                """
            )

        return self._connection

    async def close_connection(self):
        self._connection.close()


class PostgresDataBaseManager(DataBaseManager):
    pass



