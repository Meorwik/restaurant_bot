from utils.set_bot_commands import set_default_commands
from aiogram import executor, Bot, Dispatcher
from data.config import ADMINS
from app_init import init_app
from loader import dp
import handlers


async def on_startup(dispatcher: Dispatcher):
    await init_app()
    await set_default_commands(dispatcher)


async def on_shutdown(dispatcher: Dispatcher):
    bot: Bot = dispatcher.bot
    await bot.send_message(chat_id=ADMINS[0], text="bot лег")


if __name__ == '__main__':

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True, on_shutdown=on_shutdown)
