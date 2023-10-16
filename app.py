from utils.set_bot_commands import set_default_commands
from app_init import init_app
from aiogram import executor
from loader import dp
import handlers


async def on_startup(dispatcher):
    await init_app()
    await set_default_commands(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
