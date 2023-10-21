from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loader import database_manager
from core.market import Category
from aiogram import types


class SimpleKeyboardsBuilder:
    __BACK_TO_MENU_CALLBACK = "[back_to_menu]"
    back_buttons_callbacks = [__BACK_TO_MENU_CALLBACK]
    go_back_text = "🔙 Назад"

    @classmethod
    def get_developer_info_keyboard(cls):
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(
            text="👨‍💻 Контактные данные",
            url="https://t.me/tyan_io")
        )
        keyboard.add(InlineKeyboardButton(text=cls.go_back_text, callback_data=cls.__BACK_TO_MENU_CALLBACK))
        return keyboard

    @classmethod
    def get_back_to_menu_callback(cls):
        return cls.__BACK_TO_MENU_CALLBACK

    @classmethod
    def filter_back_button_callback(cls, call):
        for callback in cls.back_buttons_callbacks:
            if callback in call.data:
                return callback


class Keyboard:
    _BACK_CALLBACK_PREFIX = "[back]"
    _MENU_LEVEL = "MAIN"
    _CALLBACK_SEPARATOR = ":"
    __BACK_TO_MAIN_MENU = "TO_MAIN_MENU"

    def __init__(self, row_width):
        self._keyboard = InlineKeyboardMarkup(row_width=row_width)

    @classmethod
    def get_callback_separator(cls):
        return cls._CALLBACK_SEPARATOR

    @classmethod
    def filter_callbacks(cls, call: types.CallbackQuery) -> bool:
        return \
                cls._MENU_LEVEL is not None\
                and \
                cls._MENU_LEVEL in call.data \
                and \
                cls._BACK_CALLBACK_PREFIX not in call.data

    @classmethod
    def get_menu_level(cls):
        return cls._MENU_LEVEL

    @classmethod
    def filter_back_button_callback(cls, call: types.CallbackQuery):
        if call.data == cls._BACK_CALLBACK_PREFIX + cls._CALLBACK_SEPARATOR + cls.__BACK_TO_MAIN_MENU:
            return True

    async def _create_keyboard(self):
        return True

    def _add_back_button(self):
        go_back_button = InlineKeyboardButton(
            "🔙 Назад",
            callback_data=self._BACK_CALLBACK_PREFIX + self._CALLBACK_SEPARATOR + self.__BACK_TO_MAIN_MENU
        )
        self._keyboard.add(go_back_button)

    async def get_keyboard(self) -> InlineKeyboardMarkup:
        await self._create_keyboard()
        if self._MENU_LEVEL != "MAIN":
            self._add_back_button()
        return self._keyboard


class MainMenu(Keyboard):
    __MAIN_MENU_CALLBACK_PREFIX = "[mainMenu]"
    __CATEGORIES_CALLBACK = "[categories]"
    __CONTACT_US_CALLBACK = "[contactUs]"
    _CALLBACK_SEPARATOR = ":"

    _ALL_CALLBACKS = [__CATEGORIES_CALLBACK, __CONTACT_US_CALLBACK]

    __MAIN_MENU_FACADE = {
        "📕 Категории": f"{__MAIN_MENU_CALLBACK_PREFIX}{_CALLBACK_SEPARATOR}{__CATEGORIES_CALLBACK}",
        "👥 Контакты": f"{__MAIN_MENU_CALLBACK_PREFIX}{_CALLBACK_SEPARATOR}{__CONTACT_US_CALLBACK}",
    }

    @classmethod
    def get_categories_callback(cls) -> str:
        return cls.__CATEGORIES_CALLBACK

    @classmethod
    def get_contact_us_callback(cls) -> str:
        return cls.__CONTACT_US_CALLBACK

    @classmethod
    def filter_callbacks(cls, call) -> bool:
        return cls.__MAIN_MENU_CALLBACK_PREFIX in call.data

    @classmethod
    def get_current_callback(cls, call: types.CallbackQuery) -> str:
        for callback in cls._ALL_CALLBACKS:
            if callback in call.data:
                return callback

    async def _create_keyboard(self):
        menu_buttons = [
            InlineKeyboardButton(text=key, callback_data=value)
            for key, value
            in self.__MAIN_MENU_FACADE.items()
        ]
        self._keyboard.add(*menu_buttons)


class CategoryMenu(Keyboard):
    _MENU_LEVEL = "[categories]"

    @classmethod
    async def get_current_category_id(cls, call: types.CallbackQuery) -> int:
        category_id_index: int = 1
        callback_components = call.data.split(cls._CALLBACK_SEPARATOR)
        category_id = int(callback_components[category_id_index])
        return category_id

    async def _create_keyboard(self):
        await database_manager.set_connection()
        categories_count = await database_manager.get_categories_count()
        if categories_count > 0:
            await self.__create_categories_list_keyboard()
        else:
            await self.__create_empty_categories_keyboard()

        await database_manager.close_connection()

    async def __create_categories_list_keyboard(self):
        categories = await database_manager.get_categories_list()
        category_buttons = [
            InlineKeyboardButton(
                text=category.get_name(),
                callback_data=f"{self._MENU_LEVEL}{self._CALLBACK_SEPARATOR}{category.get_id()}"
            )
            for category in categories
        ]

        self._keyboard.add(*category_buttons)

    async def __create_empty_categories_keyboard(self):
        empty_categories_list_text = "🤷🏽 Список категорий пока пуст"
        self._keyboard.add(InlineKeyboardButton(
            text=empty_categories_list_text,
            callback_data="VREMENNO !!!!")
        )


class ProductMenu(Keyboard):
    _MENU_LEVEL = "[products]"

    def __init__(self, row_width, category: Category, back_callback: str):
        super().__init__(row_width)
        self.__category = category
        self.__back_callback = back_callback

    def _add_back_button(self):
        go_back_button = InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=self.__back_callback
        )
        self._keyboard.add(go_back_button)

    async def _create_keyboard(self):
        await database_manager.set_connection()
        products_count = await database_manager.get_products_count_in_category(self.__category.get_id())
        await database_manager.close_connection()

        if products_count > 0:
            await self.__create_products_list_keyboard()
        else:
            await self.__create_empty_products_keyboard()

    async def __create_products_list_keyboard(self):
        buttons = [
            InlineKeyboardButton(
                text=product_object.get_product_name(),
                callback_data=f"{self._MENU_LEVEL}{self._CALLBACK_SEPARATOR}{product_id}"
            )
            for product_id, product_object in
            self.__category.get_products().items()
        ]
        self._keyboard.add(*buttons)

    async def __create_empty_products_keyboard(self):
        self._keyboard.add(InlineKeyboardButton(
            text="🤷🏽 Список товаров пока пуст",
            callback_data="VREMENNO !!!!")
        )


class ProductInteractionMenu(Keyboard):
    _MENU_LEVEL = "[product]"

    __ADD_PRODUCT_TO_BASKET_CALLBACK = "[AddProduct]"
    __BUY_PRODUCT_NOW_CALLBACK = "[BuyProduct]"

    def __init__(self, row_width, back_callback: str):
        super().__init__(row_width)
        self.__back_callback = back_callback

    def _add_back_button(self):
        go_back_button = InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=self.__back_callback
        )
        self._keyboard.add(go_back_button)

    async def _create_keyboard(self):
        buttons: list = []

        self._keyboard.add(*buttons)

