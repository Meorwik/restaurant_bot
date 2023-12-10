from loader import database_manager, payments_manager
from data.config import PAYMENT_TOKEN


async def init_database_tables():
    await database_manager.create_users_table()
    await database_manager.create_user_baskets_table()
    await database_manager.create_categories_table()
    await database_manager.create_products_table()


async def init_payments_token():
    """
    ROBOKASSA token as default
    :return: None
    """
    payments_manager.set_payment_token(PAYMENT_TOKEN)


async def init_app():
    await database_manager.init_pool()
    await init_payments_token()
    await init_database_tables()
