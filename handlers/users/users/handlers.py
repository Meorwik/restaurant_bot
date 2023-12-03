from keyboards.inline.inline_keyboards import \
    CategoryMenu, \
    MainMenu, \
    ProductMenu, \
    ProductInteractionMenu, \
    SimpleKeyboards, \
    Keyboard,\
    PageableKeyboard, \
    ProfileMenu,\
    BasketInteractionMenu, \
    QuantitySelectionMenu, \
    BasketProductMenu
from handlers.commands.start import open_main_menu, SHOP_PIC_PATH, MAIN_MENU_ROW_WIDTH
from core.market import Product, Category, Basket
from loader import dp, database_manager, bot
from utils.misc.logging import CLIENT_LOGGER
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto
from states.states import StateGroup
from aiogram import types

PROFILE_MENU_ROW_WIDTH = 1
BASKET_INTERACTION_MENU_ROW_WIDTH = 1
PRODUCT_LIST_ROW_WIDTH = 1
CATEGORY_LIST_ROW_WIDTH = 2
PRODUCT_INTERACTION_ROW_WIDTH = 1


async def get_user_profile_photo(call: types.CallbackQuery) -> InputMediaPhoto:
    photos_storage_index = 0
    needed_photo_resolution_index = 2
    user_profile_photos = await bot.get_user_profile_photos(user_id=call.from_user.id, limit=1)
    photo_file_id = user_profile_photos["photos"][photos_storage_index][needed_photo_resolution_index]["file_id"]
    return InputMediaPhoto(photo_file_id)


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

            if await category_menu.get_menu_level() in call.data:
                current_menu = category_menu

        if "Product_menu" in data:
            product_menu: PageableKeyboard = data["Product_menu"]

            if await product_menu.get_menu_level() in call.data:
                current_menu = product_menu

        if "Basket_product_menu" in data:
            basket_product_menu: PageableKeyboard = data["Basket_product_menu"]

            if await basket_product_menu.get_menu_level() in call.data:
                current_menu = basket_product_menu

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

        if "Basket_product_menu" in data:
            if await current_menu.get_menu_level() == await basket_product_menu.get_menu_level():
                data["Basket_product_menu"] = current_menu

    await call.message.edit_reply_markup(await current_menu.get_keyboard())


# ________________________________MAIN MENU HANDLER____________________________________
@dp.callback_query_handler(lambda call: MainMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_main_menu(call: types.CallbackQuery, state: FSMContext):
    main_menu = MainMenu(MAIN_MENU_ROW_WIDTH)
    current_callback = main_menu.get_current_callback(call)
    categories_callback = main_menu.categories_callback
    contact_us_callback = main_menu.contact_us_callback
    open_profile_callback = main_menu.open_profile_callback

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
        simple_keyboard = SimpleKeyboards()
        about_developer_text = "Проконсультироваться или получить аудит можно в личных сообщениях 👇"
        about_developer_picture_path = "data/pictures/about_us.png"

        with open(about_developer_picture_path, "rb") as picture:
            await call.message.edit_media(InputMediaPhoto(picture))
            await call.message.edit_caption(
                caption=about_developer_text,
                reply_markup=simple_keyboard.get_developer_info_keyboard()
            )

    elif current_callback == open_profile_callback:
        user_id = await database_manager.get_user_id(call.from_user.id)
        user_profile_text = f"️⚙️ ️<b>Ваш профиль:</b>\n\n<b>Ваш ID:</b> {user_id}\n<b>Ваш телеграм ID:</b> {call.from_user.id}"
        async with state.proxy() as data:
            data["To_profile_menu"] = call.data
        profile_menu = ProfileMenu(PROFILE_MENU_ROW_WIDTH)
        profile_photo = await get_user_profile_photo(call)
        await call.message.edit_media(profile_photo)
        await call.message.edit_caption(
            caption=user_profile_text,
            reply_markup=await profile_menu.get_keyboard(),
            parse_mode=types.ParseMode.HTML
        )


# ________________________________CATEGORY MENU HANDLER___________________________________________
@dp.callback_query_handler(lambda call: CategoryMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_category_menu(call: types.CallbackQuery, state: FSMContext):
    category_id = await CategoryMenu.get_current_category_id(call)
    current_category: Category = await database_manager.get_category_with_products(category_id=category_id)

    async with state.proxy() as data:
        data["current_category"] = current_category
        back_callback = data["To_category_list"]
        data["To_product_list"] = call.data

    product_menu = ProductMenu(
        row_width=PRODUCT_LIST_ROW_WIDTH,
        storage=current_category,
        back_callback=back_callback
    )

    category_pic = current_category.picture
    if category_pic is not None:
        await call.message.edit_media(category_pic)
    else:
        await reset_shop_picture(call)

    product_menu_keyboard = await product_menu.get_keyboard()

    async with state.proxy() as data:
        data["Product_menu"] = product_menu

    await call.message.edit_caption(
        caption=f"<b>Выбранная категория:</b> <em>{current_category.name}</em>\n\n⬇️Список товаров⬇️",
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
        current_category: Category = data["current_category"]
        back_callback = data["To_product_list"]
        data["To_current_product"] = call.data

    product_interaction_keyboard = await ProductInteractionMenu(
        row_width=PRODUCT_INTERACTION_ROW_WIDTH,
        back_callback=back_callback).get_keyboard()

    for product_id in current_category.get_products_ids():
        if product_id in call.data:
            product_to_show: Product = current_category.get_product(product_id)
            if product_to_show is not None:
                async with state.proxy() as data:
                    data["current_product"] = product_to_show

                product_picture = InputMediaPhoto(product_to_show.picture)
                await call.message.edit_media(product_picture)
                await call.message.edit_caption(
                    caption=product_showcase_template.format(
                        product_id=product_to_show.id,
                        product_name=product_to_show.name,
                        product_description=product_to_show.description,
                        product_cost=product_to_show.cost
                    ),
                    reply_markup=product_interaction_keyboard
                )

            else:
                await call.answer("Произошла ошибка!\nКод ошибки: 000 (NONE)")
                CLIENT_LOGGER.error(msg="PRODUCT EXCEPTION ACCRUED (errorCode: 000) -> None")


# _____________________________PRODUCT INTERACTION MENU HANDLER___________________________________
@dp.callback_query_handler(lambda call: ProductInteractionMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_product_interaction_menu(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        back_to_products_menu_callback = data["To_product_list"]
        back_to_product_menu_callback = data["To_current_product"]

    product_interaction_menu = ProductInteractionMenu(PRODUCT_INTERACTION_ROW_WIDTH, back_to_products_menu_callback)
    current_callback = product_interaction_menu.get_current_callback(call)
    buy_now_callback = product_interaction_menu.buy_product_now_callback
    add_to_basket_callback = product_interaction_menu.add_product_to_basket_callback

    if current_callback == buy_now_callback:
        """
        BUY NOW FUNCTION 
        """
        ...

    elif current_callback == add_to_basket_callback:
        quantity_selection_menu = QuantitySelectionMenu(back_to_product_menu_callback)
        async with state.proxy() as data:
            data["quantity_selection_menu"] = quantity_selection_menu

        await call.message.edit_reply_markup(await quantity_selection_menu.get_keyboard())


@dp.callback_query_handler(lambda call: QuantitySelectionMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_quantity_selection_menu(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if "To_product_list" in data:
            back_callback = data["To_product_list"]

        quantity_selection_menu: QuantitySelectionMenu = data["quantity_selection_menu"]
        current_product: Product = data["current_product"]
        if "quantity_selection_status" in data:
            quantity_selection_status = data["quantity_selection_status"]

    plus_one_callback = quantity_selection_menu.plus_one_callback
    minus_one_callback = quantity_selection_menu.minus_one_callback
    approve_callback = quantity_selection_menu.approve_callback
    current_callback = quantity_selection_menu.get_current_callback(call)

    if current_callback == plus_one_callback:
        if quantity_selection_menu.plus_one():
            await call.message.edit_reply_markup(await quantity_selection_menu.get_keyboard())

    elif current_callback == minus_one_callback:
        if quantity_selection_menu.minus_one():
            await call.message.edit_reply_markup(await quantity_selection_menu.get_keyboard())

    elif current_callback == approve_callback:
        user_id = await database_manager.get_user_id(call.from_user.id)
        basket: Basket = await database_manager.get_user_basket(user_id)
        if quantity_selection_status is None:
            basket.add_product(current_product, quantity_selection_menu.current_quantity)

        else:
            product_to_modify = basket.get_product(current_product.id)
            product_to_modify.set_quantity(quantity_selection_menu.current_quantity)
            basket.replace_product(current_product.id, product_to_modify)
            back_callback = quantity_selection_menu.get_back_callback()
            await call.message.edit_caption(basket.get_showcase_text(product_to_modify.id))

        await database_manager.update_user_basket(basket, user_id)
        await call.answer("✅ Готово! ✅")
        await call.message.edit_reply_markup(
            reply_markup=SimpleKeyboards().get_done_button(back_callback)
        )

    async with state.proxy() as data:
        data["quantity_selection_menu"] = quantity_selection_menu


# ______________________________ PROFILE MENU HANDLER ____________________________________________
@dp.callback_query_handler(lambda call: ProfileMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_profile_menu(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        back_callback = data["To_profile_menu"]

    profile_menu = ProfileMenu(PROFILE_MENU_ROW_WIDTH)
    current_callback = profile_menu.get_current_callback(call)
    basket_callback = profile_menu.open_basket_callback

    if current_callback == basket_callback:
        async with state.proxy() as data:
            data["To_basket_menu"] = call.data

        user_id = await database_manager.get_user_id(call.from_user.id)
        basket: Basket = await database_manager.get_user_basket(user_id)

        if basket.is_empty():
            await call.message.edit_caption(
                caption=Basket.get_empty_basket_case_text(),
                reply_markup=SimpleKeyboards().get_back_button(back_callback)
            )

        else:
            basket_interaction_menu = BasketInteractionMenu(BASKET_INTERACTION_MENU_ROW_WIDTH, back_callback)
            await call.message.edit_caption(
                caption=basket.get_showcase_text(),
                reply_markup=await basket_interaction_menu.get_keyboard()
            )


# ______________________________ BASKET INTERACTION HANDLER _________________________________________
@dp.callback_query_handler(lambda call: BasketInteractionMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_basket_interaction_menu(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        back_to_profile_callback = data["To_profile_menu"]
        back_to_basket_callback = data["To_basket_menu"]

    basket_interaction_menu = BasketInteractionMenu(BASKET_INTERACTION_MENU_ROW_WIDTH, back_to_profile_callback)
    current_callback = basket_interaction_menu.get_current_callback(call)
    user_id = await database_manager.get_user_id(call.from_user.id)
    basket: Basket = await database_manager.get_user_basket(user_id)
    basket_product_menu = BasketProductMenu(storage=basket, back_callback=back_to_basket_callback)

    buy_all_products_callback = basket_interaction_menu.buy_all_products_callback
    buy_one_product_callback = basket_interaction_menu.buy_one_product_callback
    modify_product_quantity_callback = basket_interaction_menu.modify_product_quantity_callback
    delete_one_product_callback = basket_interaction_menu.delete_one_product_callback
    clear_basket_callback = basket_interaction_menu.clear_basket_callback

    choose_product_text = BasketProductMenu.get_choose_product_text()

    if current_callback == buy_all_products_callback:
        """
        Here is some logic for buying all basket for all it's cost, now I need to get payments info for continuing
        """
        ...

    elif current_callback == buy_one_product_callback:
        await call.message.edit_caption(
            caption=choose_product_text,
            reply_markup=await basket_product_menu.get_keyboard()
        )
        async with state.proxy() as data:
            data["action_to_product"] = buy_one_product_callback

    elif current_callback == modify_product_quantity_callback:
        await call.message.edit_caption(
            caption=choose_product_text,
            reply_markup=await basket_product_menu.get_keyboard()
        )
        async with state.proxy() as data:
            data["action_to_product"] = modify_product_quantity_callback

    elif current_callback == delete_one_product_callback:
        await call.message.edit_caption(
            caption=choose_product_text,
            reply_markup=await basket_product_menu.get_keyboard()
        )
        async with state.proxy() as data:
            data["action_to_product"] = delete_one_product_callback

    elif current_callback == clear_basket_callback:
        await database_manager.clear_basket(user_id)
        await call.message.edit_caption(
            caption=Basket.get_empty_basket_case_text(),
            reply_markup=SimpleKeyboards().get_back_button(back_to_profile_callback)
        )

    async with state.proxy() as data:
        data["Basket_product_menu"] = basket_product_menu


@dp.callback_query_handler(lambda call: BasketProductMenu.filter_callbacks(call), state=StateGroup.in_market)
async def handle_basket_product_menu(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        back_to_basket_callback = data["To_basket_menu"]

    basket_interaction_menu = BasketInteractionMenu(BASKET_INTERACTION_MENU_ROW_WIDTH, back_to_basket_callback)
    buy_one_product_callback = basket_interaction_menu.buy_one_product_callback
    modify_product_quantity_callback = basket_interaction_menu.modify_product_quantity_callback
    delete_one_product_callback = basket_interaction_menu.delete_one_product_callback
    current_product = None
    action = None

    user_id = await database_manager.get_user_id(call.from_user.id)
    basket: Basket = await database_manager.get_user_basket(user_id)

    for product in basket.products:
        if str(product.id) in call.data:
            current_product = basket.get_product(product.id)
            break

    if current_product is not None:
        async with state.proxy() as data:
            action = data["action_to_product"]

    if action == buy_one_product_callback:
        """
        Here is some logic for buying all basket for all it's cost, now I need to get payments info for continuing
        """
        ...

    elif action == modify_product_quantity_callback:
        quantity_selection_menu = QuantitySelectionMenu(back_to_basket_callback)
        await call.message.edit_caption(
            caption=basket.get_showcase_text(current_product.id),
            reply_markup=await quantity_selection_menu.get_keyboard()
        )
        async with state.proxy() as data:
            data["quantity_selection_status"] = "modify"
            data["quantity_selection_menu"] = quantity_selection_menu
            data["current_product"] = current_product

    elif action == delete_one_product_callback:
        basket.delete_product(current_product.id)
        basket_product_menu = BasketProductMenu(basket, back_to_basket_callback)
        await database_manager.update_user_basket(basket, user_id)
        await call.message.edit_reply_markup(await basket_product_menu.get_keyboard())

    else:
        await call.message.edit_caption(
            "ERROR: 001 (NoneProduct)"
        )



