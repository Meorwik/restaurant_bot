from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.market import ProductStorage
from loader import database_manager
from aiogram import types

EXCEPTIOM_SIGN = "&"

# --------------------------------------------------------------------------------------------------
# EXCEPTIOM_SIGN is used for buttons callbacks that ARE NOT related with opening next menu level
# --------------------------------------------------------------------------------------------------


class Keyboard:
    _BACK_CALLBACK_PREFIX = "[back]"
    _CALLBACK_SEPARATOR = ":"
    __BACK_TO_MAIN_MENU = "TO_MAIN_MENU"
    _BACK_BUTTON_TEXT = "🔙 Назад"
    _BACK_BUTTON_CALLBACK = _BACK_CALLBACK_PREFIX + _CALLBACK_SEPARATOR + __BACK_TO_MAIN_MENU

    _menu_level = "[mainMenu]"

    def __init_keyboard(self, row_width):
        self._keyboard = None
        keyboard = InlineKeyboardMarkup(row_width)
        return keyboard

    def __init__(self, row_width: int, back_callback: str = None):
        self.__keyboard_row_width = row_width
        self._keyboard = self.__init_keyboard(self.__keyboard_row_width)
        if back_callback is None:
            self._back_callback = self._BACK_BUTTON_CALLBACK
        else:
            self._back_callback = back_callback

    def get_back_callback(self):
        return self._back_callback

    @classmethod
    def filter_callbacks(cls, call: types.CallbackQuery) -> bool:
        return cls._menu_level is not None and \
                cls._menu_level in call.data and \
                cls._BACK_CALLBACK_PREFIX not in call.data and \
                EXCEPTIOM_SIGN not in call.data

    @classmethod
    def filter_back_button_callback(cls, call: types.CallbackQuery) -> bool:
        return call.data == cls._BACK_BUTTON_CALLBACK

    def _add_back_button(self):
        go_back_button = InlineKeyboardButton(
            text=self._BACK_BUTTON_TEXT,
            callback_data=self._back_callback
        )
        self._keyboard.add(go_back_button)

    def _create_empty_list_keyboard(self):
        self._keyboard.add(InlineKeyboardButton(
            text="🤷🏽 Список пока пуст",
            callback_data=self._back_callback)
        )

    async def _create_keyboard(self):
        return True

    async def get_menu_level(self):
        return self._menu_level

    async def get_keyboard(self) -> InlineKeyboardMarkup:
        self._keyboard = self.__init_keyboard(self.__keyboard_row_width)
        await self._create_keyboard()
        if self._menu_level != "[mainMenu]":
            self._add_back_button()
        return self._keyboard


class FacadeKeyboard(Keyboard):
    _ALL_CALLBACKS = []

    _MENU_FACADE = {
        "Temp1": "Temp1_callback",
        "Temp2": "Temp2_callback"
    }

    async def _create_keyboard(self):
        menu_buttons = [
            InlineKeyboardButton(text=key, callback_data=value)
            for key, value
            in self._MENU_FACADE.items()
        ]
        self._keyboard.add(*menu_buttons)

    def get_current_callback(self, call: types.CallbackQuery) -> str:
        for callback in self._ALL_CALLBACKS:
            if callback in call.data:
                return callback


class SimpleKeyboards(Keyboard):
    _SIMPLE_KEYBOARDS_ROW_WIDTH = 1

    def __init__(self):
        super().__init__(row_width=self._SIMPLE_KEYBOARDS_ROW_WIDTH)

    def get_developer_info_keyboard(self):
        contacts_button = InlineKeyboardButton(text="👨‍💻 Контактные данные", url="https://t.me/youjintyan")
        self._keyboard.add(contacts_button)
        self._add_back_button()
        return self._keyboard

    def get_back_button_keyboard(self, back_callback: str = None):
        self._keyboard.add(self.get_back_button(back_callback))
        return self._keyboard

    def get_back_button(self, back_callback: str = None):
        if back_callback is None:
            back_callback = Keyboard._BACK_BUTTON_CALLBACK

        return InlineKeyboardButton(text=self._BACK_BUTTON_TEXT, callback_data=back_callback)

    def get_payment_keyboard(self, total_cost: str, back_callback: str = None):
        self._keyboard.add(InlineKeyboardButton(
            text=f"Заплатить KZT {total_cost}",
            pay=True
        ))
        self._keyboard.add(self.get_back_button(back_callback))
        return self._keyboard


class MainMenu(FacadeKeyboard):
    _categories_callback = "[categories]"
    _contact_us_callback = "[contactUs]"
    _open_profile_callback = "[openProfile]"
    _open_basket_callback = "[openBasket]"
    _menu_level = "[mainMenu]"

    _ALL_CALLBACKS = [_categories_callback, _contact_us_callback, _open_profile_callback, _open_basket_callback]

    _MENU_FACADE = {
        "📕 Категории": f"{_menu_level}{Keyboard._CALLBACK_SEPARATOR}{_categories_callback}",
        "👤 Мой профиль": f"{_menu_level}{Keyboard._CALLBACK_SEPARATOR}{_open_profile_callback}",
        "👥 Контакты": f"{_menu_level}{Keyboard._CALLBACK_SEPARATOR}{_contact_us_callback}",
        "🛍 Корзина": f"{_menu_level}{Keyboard._CALLBACK_SEPARATOR}{_open_basket_callback}",
    }

    @property
    def categories_callback(self) -> str:
        return self._categories_callback

    @property
    def contact_us_callback(self) -> str:
        return self._contact_us_callback

    @property
    def open_profile_callback(self) -> str:
        return self._open_profile_callback

    @property
    def open_basket_callback(self):
        return self._open_basket_callback


class PageableKeyboard(Keyboard):
    __MIN_PAGE_NUMBER = 1
    __PREVIOUS_PAGE_CALLBACK = "[<<<]"
    __NEXT_PAGE_CALLBACK = "[>>>]"

    @classmethod
    def filter_page_callbacks(cls, call: types.CallbackQuery) -> bool:
        return cls.__PREVIOUS_PAGE_CALLBACK in call.data or cls.__NEXT_PAGE_CALLBACK in call.data

    def get_previous_page_callback(self):
        return self._menu_level + self._CALLBACK_SEPARATOR + self.__PREVIOUS_PAGE_CALLBACK + EXCEPTIOM_SIGN

    def get_next_page_callback(self):
        return self._menu_level + self._CALLBACK_SEPARATOR + self.__NEXT_PAGE_CALLBACK + EXCEPTIOM_SIGN

    def open_next_page(self):
        if self._current_page == self._max_page_count:
            self._current_page = self.__MIN_PAGE_NUMBER
            self.__separator = 0
        else:
            self._current_page += 1
            self.__separator += self._max_elements_on_page

    def open_prev_page(self):
        if self._current_page == self.__MIN_PAGE_NUMBER:
            self._current_page = self._max_page_count
            self.__separator = self._max_elements_on_page
        else:
            self._current_page -= 1
            self.__separator -= self._max_elements_on_page

    def __init__(self, row_width: int, max_elements_on_page: int = 5, back_callback: str = None):
        super().__init__(row_width=row_width, back_callback=back_callback)
        self._max_elements_on_page = max_elements_on_page
        self._current_page = 1
        self.__separator = 0
        self._buttons_storage = []
        self._max_page_count = None

    def _set_max_page_count(self):
        self._max_page_count = self.__count_max_pages()
        return self._max_page_count

    def _create_page_buttons(self):
        open_previous_page_text = "««"
        current_page_text = str(self._current_page)
        open_next_page_text = "»»"

        open_previous_page_button = InlineKeyboardButton(
            text=open_previous_page_text,
            callback_data=self.get_previous_page_callback()
        )
        current_page_button = InlineKeyboardButton(
            text=current_page_text,
            callback_data=current_page_text
        )
        open_next_page_button = InlineKeyboardButton(
            text=open_next_page_text,
            callback_data=self.get_next_page_callback()
        )

        self._keyboard.row(
            open_previous_page_button,
            current_page_button,
            open_next_page_button
        )

    def __count_max_pages(self):
        buttons_count = len(self._buttons_storage)
        pages_not_round = buttons_count / self._max_elements_on_page
        pages = int(pages_not_round)
        if pages_not_round % 1 != 0:
            pages += 1
        return pages

    def get_buttons_to_show(self):
        return self._buttons_storage[self.__separator: self.__separator + self._max_elements_on_page]

    async def _create_keyboard(self):
        await self._create_buttons()
        elements_count = len(self._buttons_storage)
        if elements_count > 0:
            if elements_count > self._max_elements_on_page:
                self._set_max_page_count()
                self._keyboard.add(*self.get_buttons_to_show())
                self._create_page_buttons()

            else:
                self._keyboard.add(*self._buttons_storage)

        else:
            self._create_empty_list_keyboard()

    async def _create_buttons(self):
        """
        your buttons must be created here
        """
        buttons = [...]
        self._buttons_storage = buttons
        return self._buttons_storage


class CategoryMenu(PageableKeyboard):
    _menu_level = "[categories]"
    __MAX_CATEGORIES_COUNT_ON_PAGE = 6

    def __init__(self, row_width):
        super().__init__(row_width=row_width, max_elements_on_page=self.__MAX_CATEGORIES_COUNT_ON_PAGE)

    @classmethod
    async def get_current_category_id(cls, call: types.CallbackQuery) -> int:
        category_id_index: int = 1
        callback_components = call.data.split(cls._CALLBACK_SEPARATOR)
        category_id = int(callback_components[category_id_index])
        return category_id

    async def _create_buttons(self):
        categories = await database_manager.get_categories_list()
        buttons = [
            InlineKeyboardButton(
                text=category.name,
                callback_data=f"{self._menu_level}{self._CALLBACK_SEPARATOR}{category.id}")
            for category in categories
        ]
        self._buttons_storage = buttons


class ProductMenu(PageableKeyboard):
    _menu_level = "[products]"
    __MAX_PRODUCTS_COUNT_ON_PAGE = 5

    def __init__(self, row_width: int, storage: ProductStorage, back_callback: str = None):
        super().__init__(
            row_width=row_width,
            max_elements_on_page=self.__MAX_PRODUCTS_COUNT_ON_PAGE,
            back_callback=back_callback
        )
        self._product_storage = storage

    async def _create_buttons(self):
        buttons = [
            InlineKeyboardButton(
                text=f"{product_object.name} | {product_object.cost} Тг",
                callback_data=f"{self._menu_level}{self._CALLBACK_SEPARATOR}{product_object.id}"
            )
            for product_object in
            self._product_storage.products
        ]
        self._buttons_storage = buttons


class ProductInteractionMenu(FacadeKeyboard):
    _menu_level = "[product]"

    __ADD_PRODUCT_TO_BASKET_CALLBACK = "[AddProductToBasket]"
    __BUY_PRODUCT_NOW_CALLBACK = "[BuyProductNow]"

    _ALL_CALLBACKS = [__ADD_PRODUCT_TO_BASKET_CALLBACK, __BUY_PRODUCT_NOW_CALLBACK]

    _MENU_FACADE = {
        "Купить сейчас": f"{_menu_level}{Keyboard._CALLBACK_SEPARATOR}{__BUY_PRODUCT_NOW_CALLBACK}",
        "Добавить в корзину": f"{_menu_level}{Keyboard._CALLBACK_SEPARATOR}{__ADD_PRODUCT_TO_BASKET_CALLBACK}"
    }

    @property
    def add_product_to_basket_callback(self):
        return self.__ADD_PRODUCT_TO_BASKET_CALLBACK

    @property
    def buy_product_now_callback(self):
        return self.__BUY_PRODUCT_NOW_CALLBACK

    def __init__(self, row_width, back_callback: str):
        super().__init__(row_width)
        self._back_callback = back_callback


class QuantitySelectionMenu(FacadeKeyboard):
    __QUANTITY_SELECTION_MENU_ROW_WIDTH = 3

    _menu_level = "[productQuantitySelection]"

    __MINUS_ONE_TEXT = "-"
    __PLUS_ONE_TEXT = "+"
    __APPROVE_TEXT = "✅ Подтвердить"

    __PLUS_ONE_CALLBACK = "[PlusOne]"
    __MINUS_ONE_CALLBACK = "[MinusOne]"
    __APPROVE_CALLBACK = "[Approve]"

    _ALL_CALLBACKS = [__MINUS_ONE_CALLBACK, __PLUS_ONE_CALLBACK, __APPROVE_CALLBACK]

    def __init__(self, back_callback):
        self.__current_quantity = 1
        super().__init__(row_width=self.__QUANTITY_SELECTION_MENU_ROW_WIDTH)
        self._back_callback = back_callback
        self.__update_facade()

    def __update_facade(self):
        self.__facade = {
            f"{self.__MINUS_ONE_TEXT}": f"{self._menu_level}{Keyboard._CALLBACK_SEPARATOR}{self.__MINUS_ONE_CALLBACK}",
            f"{self.__current_quantity}": f"{self._menu_level}{Keyboard._CALLBACK_SEPARATOR}{str(self.__current_quantity)}",
            f"{self.__PLUS_ONE_TEXT}": f"{self._menu_level}{Keyboard._CALLBACK_SEPARATOR}{self.__PLUS_ONE_CALLBACK}",
        }
        return True

    async def _create_keyboard(self):
        self.__update_facade()
        selection_buttons = [
            InlineKeyboardButton(key, callback_data=value) for
            key, value in
            self.__facade.items()
        ]
        self._keyboard.row(*selection_buttons)

        approve = InlineKeyboardButton(
            text=f"{self.__APPROVE_TEXT}",
            callback_data=f"{self._menu_level}{Keyboard._CALLBACK_SEPARATOR}{self.__APPROVE_CALLBACK}"
        )
        self._keyboard.add(approve)

    @property
    def plus_one_callback(self):
        return self.__PLUS_ONE_CALLBACK

    @property
    def minus_one_callback(self):
        return self.__MINUS_ONE_CALLBACK

    @property
    def approve_callback(self):
        return self.__APPROVE_CALLBACK

    @property
    def current_quantity(self):
        return self.__current_quantity

    def plus_one(self):
        self.__current_quantity += 1
        return True

    def minus_one(self):
        if self.__current_quantity > 1:
            self.__current_quantity -= 1
            return True
        else:
            self.__current_quantity = 1
            return False


class ProfileMenu(FacadeKeyboard):
    _menu_level = "[profile]"
    __OPEN_BASKET_CALLBACK = "[OpenBasket]"
    _ALL_CALLBACKS = [__OPEN_BASKET_CALLBACK]

    _MENU_FACADE = {
        "🛍 Посмотреть корзину": f"{_menu_level}{Keyboard._CALLBACK_SEPARATOR}{__OPEN_BASKET_CALLBACK}",
    }

    _profile_showcase_template = \
        "️⚙️ ️<b>Ваш профиль:</b>\n\n<b>Ваш ID:</b> {user_id}\n<b>Ваш телеграм ID:</b> {telegram_id}"

    @classmethod
    def get_profile_showcase_template(cls):
        return cls._profile_showcase_template

    def __init__(self, row_width, back_callback: str = None):
        super().__init__(row_width)
        if back_callback is not None:
            self._back_callback = back_callback

    @property
    def open_basket_callback(self):
        return self.__OPEN_BASKET_CALLBACK


class BasketInteractionMenu(FacadeKeyboard):
    _menu_level = "[basket]"

    __BUY_ALL_PRODUCTS_CALLBACK = "[BuyAllProducts]"
    __BUY_ONE_PRODUCT_CALLBACK = "[BuyOneProduct]"
    __DELETE_ONE_PRODUCT_CALLBACK = "[DeleteOneProduct]"
    __MODIFY_PRODUCT_QUANTITY_CALLBACK = "[ModifyProductQuantity]"
    __CLEAR_BASKET_CALLBACK = "[ClearBasket]"

    _ALL_CALLBACKS = [
        __BUY_ALL_PRODUCTS_CALLBACK,
        __CLEAR_BASKET_CALLBACK,
        __MODIFY_PRODUCT_QUANTITY_CALLBACK,
        __DELETE_ONE_PRODUCT_CALLBACK,
        __BUY_ONE_PRODUCT_CALLBACK
    ]

    _MENU_FACADE = {
        "Купить все": f"{_menu_level}{Keyboard._CALLBACK_SEPARATOR}{__BUY_ALL_PRODUCTS_CALLBACK}",
        "Купить один товар": f"{_menu_level}{Keyboard._CALLBACK_SEPARATOR}{__BUY_ONE_PRODUCT_CALLBACK}",
        "Изменить количество товара": f"{_menu_level}{Keyboard._CALLBACK_SEPARATOR}{__MODIFY_PRODUCT_QUANTITY_CALLBACK}",
        "Удалить товар": f"{_menu_level}{Keyboard._CALLBACK_SEPARATOR}{__DELETE_ONE_PRODUCT_CALLBACK}",
        "Очистить корзину": f"{_menu_level}{Keyboard._CALLBACK_SEPARATOR}{__CLEAR_BASKET_CALLBACK}",
    }

    def __init__(self, row_width: int, back_callback: str = None):
        super().__init__(row_width)
        if back_callback is not None:
            self._back_callback = back_callback

    @property
    def buy_all_products_callback(self):
        return self.__BUY_ALL_PRODUCTS_CALLBACK

    @property
    def buy_one_product_callback(self):
        return self.__BUY_ONE_PRODUCT_CALLBACK

    @property
    def modify_product_quantity_callback(self):
        return self.__MODIFY_PRODUCT_QUANTITY_CALLBACK

    @property
    def delete_one_product_callback(self):
        return self.__DELETE_ONE_PRODUCT_CALLBACK

    @property
    def clear_basket_callback(self):
        return self.__CLEAR_BASKET_CALLBACK


class BasketProductMenu(ProductMenu):
    _menu_level = "[BasketProducts]"
    __BASKET_PRODUCT_MENU_ROW_WIDTH = 1
    __CHOOSE_PRODUCT_TEXT = "⬇️ Выберите товар из списка: ⬇️"

    @classmethod
    def get_choose_product_text(cls):
        return cls.__CHOOSE_PRODUCT_TEXT

    def __init__(self, storage: ProductStorage, back_callback: str = None):
        super().__init__(self.__BASKET_PRODUCT_MENU_ROW_WIDTH, storage, back_callback)

    async def _create_buttons(self):
        buttons = [
            InlineKeyboardButton(
                text=f"{product_object.name} ( {product_object.quantity} )-шт | {product_object.total_cost} Тг",
                callback_data=f"{self._menu_level}{self._CALLBACK_SEPARATOR}{product_object.id}"
            )
            for product_object in
            self._product_storage.products
        ]
        self._buttons_storage = buttons
