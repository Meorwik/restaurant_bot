from keyboards.inline.inline_keyboards import \
    CategoryMenu, \
    MainMenu, \
    ProductMenu, \
    ProductInteractionMenu, \
    SimpleKeyboardsBuilder, \
    Keyboard
from handlers.commands.start import open_main_menu, SHOP_PIC_PATH
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto
from loader import dp, database_manager
from states.states import StateGroup
from aiogram import types

PRODUCT_LIST_ROW_WIDTH = 2
CATEGORY_LIST_ROW_WIDTH = 2
PRODUCT_INTERACTION_ROW_WIDTH = 1


async def reset_shop_picture(call: types.CallbackQuery):
    with open(SHOP_PIC_PATH, "rb") as shop_pic:
        await call.message.edit_media(InputMediaPhoto(shop_pic))


# ________________________________BACK BUTTONS HANDLER____________________________________
@dp.callback_query_handler(
    lambda call: Keyboard.filter_back_button_callback(call) or
    SimpleKeyboardsBuilder.filter_back_button_callback(call),
    state="*"
)
async def handle_back_callbacks(call: types.CallbackQuery):
    await open_main_menu(call.message)


# ________________________________MAIN MENU HANDLER____________________________________
@dp.callback_query_handler(lambda call: MainMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_main_menu(call: types.CallbackQuery, state: FSMContext):
    current_callback = MainMenu.get_current_callback(call)
    categories_callback = MainMenu.get_categories_callback()
    contact_us_callback = MainMenu.get_contact_us_callback()

    async with state.proxy() as data:
        data["To_category_list"] = call.data

    if current_callback == categories_callback:
        categories_menu_keyboard = await CategoryMenu(CATEGORY_LIST_ROW_WIDTH).get_keyboard()
        await call.message.edit_caption(
            caption="🗂 Каталог",
            reply_markup=categories_menu_keyboard
        )

    elif current_callback == contact_us_callback:
        about_developer_text = "Проконсультироваться или получить аудит можно в личных сообщениях 👇"
        about_developer_picture_path = "data/pictures/about_us.png"

        with open(about_developer_picture_path, "rb") as picture:
            await call.message.edit_media(InputMediaPhoto(picture))
            await call.message.edit_caption(
                caption=about_developer_text,
                reply_markup=SimpleKeyboardsBuilder.get_developer_info_keyboard()
            )


# ________________________________CATEGORY MENU HANDLER____________________________________
@dp.callback_query_handler(lambda call: CategoryMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_category_menu(call: types.CallbackQuery, state: FSMContext):
    await database_manager.set_connection()
    category_id = await CategoryMenu.get_current_category_id(call)
    current_category = await database_manager.get_category_with_products(category_id=category_id)
    await database_manager.close_connection()

    async with state.proxy() as data:
        data["current_category"] = current_category
        back_callback = data["To_category_list"]
        data["To_product_list"] = call.data

    product_menu_keyboard = ProductMenu(
        row_width=PRODUCT_LIST_ROW_WIDTH,
        category=current_category,
        back_callback=back_callback
    )

    product_list_text = f"Товары категории {current_category.get_name()}"
    product_list_keyboard = await product_menu_keyboard.get_keyboard()

    category_pic = current_category.get_picture()
    if category_pic is not None:
        await call.message.edit_media(category_pic)
    else:
        await reset_shop_picture(call)

    await call.message.edit_caption(
        caption=product_list_text,
        reply_markup=product_list_keyboard
    )


# ________________________________PRODUCT MENU HANDLER____________________________________________
@dp.callback_query_handler(lambda call: ProductMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_product_menu(call: types.CallbackQuery, state: FSMContext):
    product_showcase_template = """
        Товар №**{product_id}**

        **{product_name}**

        __{product_description}__

        ЦЕНА: {product_cost} Тг
    """

    async with state.proxy() as data:
        current_category = data["current_category"]
        back_callback = data["To_product_list"]

    product_interaction_keyboard = await ProductInteractionMenu(
        row_width=PRODUCT_INTERACTION_ROW_WIDTH,
        back_callback=back_callback
    ).get_keyboard()

    for product_id in current_category.get_product_ids():
        if product_id in call.data:
            product_to_show = current_category.get_product(product_id)

            await call.message.edit_media(InputMediaPhoto(product_to_show.get_product_picture()))
            await call.message.edit_caption(
                caption=product_showcase_template.format(
                    product_id=product_to_show.get_product_id(),
                    product_name=product_to_show.get_product_name(),
                    product_description=product_to_show.get_product_description(),
                    product_cost=product_to_show.get_product_cost()
                ),
                parse_mode="Markdown",
                reply_markup=product_interaction_keyboard
            )


# _____________________________PRODUCT INTERACTION HANDLER______________________________


