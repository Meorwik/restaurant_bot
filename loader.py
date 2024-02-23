from utils.db_api.connection_configs import get_connection_config
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from utils.development_tools.tools import PaymentsManager
from utils.db_api.db_api import PostgresDataBaseManager
from aiogram import Bot, Dispatcher, types
from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

current_config = get_connection_config()
database_manager = PostgresDataBaseManager(current_config)
payments_manager = PaymentsManager(bot)

