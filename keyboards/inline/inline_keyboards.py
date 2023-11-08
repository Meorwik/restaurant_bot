from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loader import database_manager
from core.market import Category
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
    __BACK_BUTTON_CALLBACK = _BACK_CALLBACK_PREFIX + _CALLBACK_SEPARATOR + __BACK_TO_MAIN_MENU

    _menu_level = "MAIN"

    def __init_keyboard(self, row_width):
        self._keyboard = None
        keyboard = InlineKeyboardMarkup(row_width)
        return keyboard

    def __init__(self, row_width: int):
        self.__keyboard_row_width = row_width
        self._keyboard = self.__init_keyboard(self.__keyboard_row_width)
        self._back_callback = self.__BACK_BUTTON_CALLBACK

    @classmethod
    def filter_callbacks(cls, call: types.CallbackQuery) -> bool:
        return cls._menu_level is not None and \
                cls._menu_level in call.data and \
                cls._BACK_CALLBACK_PREFIX not in call.data and \
                EXCEPTIOM_SIGN not in call.data

    @classmethod
    def filter_back_button_callback(cls, call: types.CallbackQuery) -> bool:
        return call.data == cls.__BACK_BUTTON_CALLBACK

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
        if self._menu_level != "MAIN":
            self._add_back_button()
        return self._keyboard


class MainMenu(Keyboard):
    _categories_callback = "[categories]"
    _contact_us_callback = "[contactUs]"
    __MAIN_MENU_CALLBACK_PREFIX = "[mainMenu]"

    _ALL_CALLBACKS = [_categories_callback, _contact_us_callback]

    __MAIN_MENU_FACADE = {
        "📕 Категории": f"{__MAIN_MENU_CALLBACK_PREFIX}{Keyboard._CALLBACK_SEPARATOR}{_categories_callback}",
        "👥 Контакты": f"{__MAIN_MENU_CALLBACK_PREFIX}{Keyboard._CALLBACK_SEPARATOR}{_contact_us_callback}",
    }

    @property
    def categories_callback(self) -> str:
        return self._categories_callback

    @property
    def contact_us_callback(self) -> str:
        return self._contact_us_callback

    @classmethod
    def filter_callbacks(cls, call) -> bool:
        return cls.__MAIN_MENU_CALLBACK_PREFIX in call.data

    def get_current_callback(self, call: types.CallbackQuery) -> str:
        for callback in self._ALL_CALLBACKS:
            if callback in call.data:
                return callback

    async def _create_keyboard(self):
        menu_buttons = [
            InlineKeyboardButton(text=key, callback_data=value)
            for key, value
            in self.__MAIN_MENU_FACADE.items()
        ]
        self._keyboard.add(*menu_buttons)


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
            self.__separator = len(self._buttons_storage) - self._max_elements_on_page
        else:
            self._current_page -= 1
            self.__separator -= self._max_elements_on_page

    def __init__(self, row_width, max_elements_on_page=5):
        super().__init__(row_width=row_width)
        self._max_page_count = None
        self._max_elements_on_page = max_elements_on_page
        self._current_page = 1
        self.__separator = 0
        self._buttons_storage = []

    def _set_max_pages_count(self):
        self._max_page_count = self.__count_max_pages()

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

    async def _create_keyboard(self):
        categories_count = await database_manager.get_categories_count()
        if categories_count > 0:
            await self.__create_categories_buttons()

            if categories_count > self.__MAX_CATEGORIES_COUNT_ON_PAGE:
                self._set_max_pages_count()
                self._keyboard.add(*self.get_buttons_to_show())
                self._create_page_buttons()

            else:
                self._keyboard.add(*self._buttons_storage)

        else:
            self._create_empty_list_keyboard()

    async def __create_categories_buttons(self):
        categories = await database_manager.get_categories_list()
        buttons = [
            InlineKeyboardButton(
                text=category.get_name(),
                callback_data=f"{self._menu_level}{self._CALLBACK_SEPARATOR}{category.get_id()}")
            for category in categories
        ]
        self._buttons_storage = buttons


class ProductMenu(PageableKeyboard):
    _menu_level = "[products]"
    __MAX_PRODUCTS_COUNT_ON_PAGE = 5

    def __init__(self, row_width: int, category: Category, back_callback: str):
        super().__init__(row_width=row_width, max_elements_on_page=self.__MAX_PRODUCTS_COUNT_ON_PAGE)
        self.__category = category
        self._back_callback = back_callback

    async def _create_keyboard(self):
        products_count = await database_manager.count_products_in_category(self.__category.get_id())
        if products_count > 0:
            await self.__create_products_buttons()

            if products_count > self.__MAX_PRODUCTS_COUNT_ON_PAGE:
                self._set_max_pages_count()
                self._keyboard.add(*self.get_buttons_to_show())
                self._create_page_buttons()

            else:
                self._keyboard.add(*self._buttons_storage)

        else:
            self._create_empty_list_keyboard()

    async def __create_products_buttons(self):
        buttons = [
            InlineKeyboardButton(
                text=f"{product_object.get_name()} | {product_object.get_cost()} Тг",
                callback_data=f"{self._menu_level}{self._CALLBACK_SEPARATOR}{product_id}"
            )
            for product_id, product_object in
            self.__category.get_products().items()
        ]
        self._buttons_storage = buttons


class ProductInteractionMenu(Keyboard):
    _menu_level = "[product]"

    __ADD_PRODUCT_TO_BASKET_CALLBACK = "[AddProduct]"
    __BUY_PRODUCT_NOW_CALLBACK = "[BuyProduct]"

    def __init__(self, row_width, back_callback: str):
        super().__init__(row_width)
        self._back_callback = back_callback


class SimpleKeyboards(Keyboard):
    _SIMPLE_KEYBOARDS_ROW_WIDTH = 1

    def __init__(self):
        super().__init__(row_width=self._SIMPLE_KEYBOARDS_ROW_WIDTH)

    def get_developer_info_keyboard(self):
        contacts_button = InlineKeyboardButton(text="👨‍💻 Контактные данные", url="https://t.me/youjintyan")
        self._keyboard.add(contacts_button)
        self._add_back_button()
        return self._keyboard
