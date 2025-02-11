from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.inline.inline_keyboards import MainMenu
from aiogram.types import InputMediaPhoto
from loader import dp, database_manager
from states.states import StateGroup
from aiogram import types
from typing import Final

SHOP_PIC_PATH: Final[str] = "data/pictures/pizza_hut.png"
MAIN_MENU_ROW_WIDTH: Final[int] = 1


async def get_greeting_text(message: types.Message):
    greeting_text = f"""
    👋 Привет {message.chat.full_name}\n💎 Главное меню:
    """
    return greeting_text


async def open_main_menu(message: types.Message):
    main_menu_keyboard = MainMenu(MAIN_MENU_ROW_WIDTH)
    keyboard = await main_menu_keyboard.get_keyboard()

    with open(SHOP_PIC_PATH, "rb") as photo:
        await message.edit_media(InputMediaPhoto(photo))
        await message.edit_caption(
            caption=await get_greeting_text(message),
            reply_markup=keyboard
        )


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message):
    if await database_manager.is_new_user(message.from_user):
        user_id = await database_manager.add_user(message.from_user)
        await database_manager.create_new_basket(user_id)

    main_menu_keyboard = MainMenu(MAIN_MENU_ROW_WIDTH)
    keyboard = await main_menu_keyboard.get_keyboard()
    await StateGroup.in_market.set()

    with open(SHOP_PIC_PATH, "rb") as photo:
        await message.answer_photo(
            photo=photo,
            caption=await get_greeting_text(message),
            reply_markup=keyboard
        )
