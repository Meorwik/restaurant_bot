from loader import database_manager


async def init_database_tables():
    await database_manager.create_users_table()
    await database_manager.create_categories_table()
    await database_manager.create_products_table()


async def init_app():
    await database_manager.init_pool()
    await init_database_tables()
