from keyboards.inline.inline_keyboards import \
    CategoryMenu, \
    MainMenu, \
    ProductMenu, \
    ProductInteractionMenu, \
    SimpleKeyboards, \
    Keyboard,\
    PageableKeyboard
from handlers.commands.start import open_main_menu, SHOP_PIC_PATH, MAIN_MENU_ROW_WIDTH
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto
from loader import dp, database_manager
from states.states import StateGroup
from aiogram import types

PRODUCT_LIST_ROW_WIDTH = 1
CATEGORY_LIST_ROW_WIDTH = 2
PRODUCT_INTERACTION_ROW_WIDTH = 1


async def reset_shop_picture(call: types.CallbackQuery):
    with open(SHOP_PIC_PATH, "rb") as shop_pic:
        await call.message.edit_media(InputMediaPhoto(shop_pic))


# ________________________________BACK BUTTONS HANDLER____________________________________
@dp.callback_query_handler(lambda call: Keyboard.filter_back_button_callback(call), state="*")
async def handle_back_callbacks(call: types.CallbackQuery):
    await open_main_menu(call.message)


# ________________________________PAGE BUTTONS HANDLER____________________________________
@dp.callback_query_handler(lambda call: PageableKeyboard.filter_page_callbacks(call), state=StateGroup.in_market)
async def handle_page_buttons(call: types.CallbackQuery, state: FSMContext):
    current_menu = None
    async with state.proxy() as data:
        if "Categories_menu" in data:
            category_menu: PageableKeyboard = data["Categories_menu"]
        if "Product_menu" in data:
            product_menu: PageableKeyboard = data["Product_menu"]

    if await category_menu.get_menu_level() in call.data:
        current_menu = category_menu

    elif await product_menu.get_menu_level() in call.data:
        current_menu = product_menu

    if call.data == current_menu.get_previous_page_callback():
        current_menu.open_prev_page()

    elif call.data == current_menu.get_next_page_callback():
        current_menu.open_next_page()

    async with state.proxy() as data:
        if "Categories_menu" in data:
            if await current_menu.get_menu_level() == await category_menu.get_menu_level():
                data["Categories_menu"] = current_menu

        if "Product_menu" in data:
            if await current_menu.get_menu_level() == await product_menu.get_menu_level():
                data["Product_menu"] = current_menu

    await call.message.edit_reply_markup(await current_menu.get_keyboard())


# ________________________________MAIN MENU HANDLER____________________________________
@dp.callback_query_handler(lambda call: MainMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_main_menu(call: types.CallbackQuery, state: FSMContext):
    main_menu = MainMenu(MAIN_MENU_ROW_WIDTH)
    current_callback = main_menu.get_current_callback(call)
    categories_callback = main_menu.categories_callback
    contact_us_callback = main_menu.contact_us_callback

    if current_callback == categories_callback:
        category_menu = CategoryMenu(CATEGORY_LIST_ROW_WIDTH)
        categories_menu_keyboard = await category_menu.get_keyboard()
        async with state.proxy() as data:
            data["To_category_list"] = call.data
            data["Categories_menu"] = category_menu

        await reset_shop_picture(call)
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
                reply_markup=SimpleKeyboards().get_developer_info_keyboard()
            )


# ________________________________CATEGORY MENU HANDLER____________________________________
@dp.callback_query_handler(lambda call: CategoryMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_category_menu(call: types.CallbackQuery, state: FSMContext):
    category_id = await CategoryMenu.get_current_category_id(call)
    current_category = await database_manager.get_category_with_products(category_id=category_id)

    async with state.proxy() as data:
        data["current_category"] = current_category
        back_callback = data["To_category_list"]
        data["To_product_list"] = call.data

    product_menu = ProductMenu(
        row_width=PRODUCT_LIST_ROW_WIDTH,
        category=current_category,
        back_callback=back_callback
    )

    category_pic = current_category.get_picture()
    if category_pic is not None:
        await call.message.edit_media(category_pic)
    else:
        await reset_shop_picture(call)

    product_menu_keyboard = await product_menu.get_keyboard()

    async with state.proxy() as data:
        data["Product_menu"] = product_menu

    await call.message.edit_caption(
        caption=f"<b>Выбранная категория:</b> <em>{current_category.get_name()}</em>\n\n⬇️Список товаров⬇️",
        reply_markup=product_menu_keyboard
    )


# ________________________________PRODUCT MENU HANDLER____________________________________________
@dp.callback_query_handler(lambda call: ProductMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_product_menu(call: types.CallbackQuery, state: FSMContext):
    product_showcase_template = """
    Товар №<b>{product_id}</b>

    Название: <b>{product_name}</b>
    
    Описание: 
    <em>{product_description}</em>

    ЦЕНА: <b>{product_cost} Тг</b>
    """

    async with state.proxy() as data:
        current_category = data["current_category"]
        back_callback = data["To_product_list"]

    product_interaction_keyboard = await ProductInteractionMenu(
        row_width=PRODUCT_INTERACTION_ROW_WIDTH,
        back_callback=back_callback).get_keyboard()

    for product_id in current_category.get_product_ids():
        if product_id in call.data:
            product_to_show = current_category.get_product(product_id)

            await call.message.edit_media(InputMediaPhoto(product_to_show.get_picture()))
            await call.message.edit_caption(
                caption=product_showcase_template.format(
                    product_id=product_to_show.get_id(),
                    product_name=product_to_show.get_name(),
                    product_description=product_to_show.get_description(),
                    product_cost=product_to_show.get_cost()
                ),
                reply_markup=product_interaction_keyboard
            )


# _____________________________PRODUCT INTERACTION HANDLER______________________________


