from loader import database_manager


async def init_db_tables():
    await database_manager.set_connection()
    await database_manager.create_users_table()
    await database_manager.create_categories_table()
    await database_manager.create_products_table()
    await database_manager.close_connection()


async def init_app():
    await init_db_tables()
