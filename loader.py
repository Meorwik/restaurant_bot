from aiogram.contrib.fsm_storage.memory import MemoryStorage
from utils.db_api.connection_configs import ConnectionConfig
from utils.db_api.db_api import PostgresDataBaseManager
from aiogram import Bot, Dispatcher, types
from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

current_db_config = ConnectionConfig.get_test_db_connection_config()
database_manager = PostgresDataBaseManager(current_db_config)

