from utils.development_tools.tools import JsonTool
from aiogram.types import InputMediaPhoto
from dataclasses import dataclass, field


@dataclass()
class BasketData:
    products: list = field(default_factory=list)
    total_cost: int = 0

    def transform_to_product_data(self):
        return [
            ProductData(
                id=product["id"],
                cost=product["cost"],
                name=product["name"],
                quantity=product["quantity"],
                is_active=product["is_active"],
                description=product["description"],
                picture=product["picture"]
            )
            for
            product in self.products
        ]


@dataclass()
class ProductData:
    id: int
    cost: int
    name: str
    quantity: int
    picture: str
    total_cost: int = field(init=False)
    description: str = field(default="null")
    is_active: bool = True

    def __repr__(self):
        return f"id-({self.id}) ProductDataObject status: {self.is_active}"

    def __post_init__(self):
        self.total_cost = self.quantity * self.cost

    def set_quantity(self, value: int):
        self.quantity = value
        self.total_cost = self.quantity * self.cost

    async def deactivate_product(self):
        self.__is_active = False

    async def activate_product(self):
        self.__is_active = True


class Product(ProductData):
    def __repr__(self):
        return f"ProductObject: {self.__name}"

    def __init__(self, product_id=None, cost=None, name=None, description=None, product_picture=None, config=None):
        self.__id = product_id
        self.__cost = cost
        self.__name = name
        self.__description = description
        self.__picture = product_picture

        if config is not None:
            for key, value in config.items():
                self.__setattr__(key, value)

    @property
    def id(self):
        return self.__id

    @property
    def cost(self):
        return int(self.__cost)

    @cost.setter
    def cost(self, value: int):
        if value > 0:
            self.__name = value
        else:
            raise Exception("Cost must be greater than zero")

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__description

    @property
    def picture(self):
        return self.__picture

    @picture.setter
    def picture(self, value):
        if value is not None:
            self.__picture = value


class ProductStorage:
    _product_showcase_template = """
    Товар №<b>{product_id}</b>

    Название: <b>{product_name}</b>

    Описание: 
    <em>{product_description}</em>

    ЦЕНА: <b>{product_cost} Тг</b>
    """

    @classmethod
    def get_product_showcase_template(cls):
        return cls._product_showcase_template

    def __init__(self):
        self.__products: list = []

    @property
    def products(self) -> list:
        return self.__products

    @products.setter
    def products(self, value: list):
        self.__products = value

    def is_empty(self) -> bool:
        return len(self.__products) < 1

    def get_product(self, product_id) -> ProductData:
        for product in self.products:
            if int(product.id) == int(product_id):
                return product


class Category(ProductStorage):
    def __repr__(self):
        return f"CategoryObject: {self._name}"

    def __init__(self,  category_id: int, name: str, picture_url=None):
        super().__init__()
        self.__id = category_id
        self._name = name

        if picture_url is not None:
            self.__picture = InputMediaPhoto(picture_url)
        else:
            self.__picture = None

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self._name

    @property
    def picture(self):
        return self.__picture

    def get_products_ids(self):
        ids = [str(product_id+1) for product_id, product in enumerate(self.products)]
        return ids

    def add_product(self, product: Product):
        self.products.append(product)


class Basket(ProductStorage):
    __empty_basket_case_text = "Ваша корзина пуста!"

    _product_showcase_template = """
    Товар №<b>{product_id}:</b>

        Название: <b>{product_name}</b>
        Количество: <em>{product_quantity}</em>
        Цена товара: <b>{product_cost} Тг</b> / 1.шт
        Общая стоимость: <b>{total_cost} Тг</b>\n\n
    """

    __total_basket_cost_text = "Общая стоимость корзины: <b>{total_cost} Тг</b>"

    def get_basket_showcase_text(self):
        basket_text_info = ""
        for product in self.products:
            basket_text_info += self.get_product_showcase_text(product.id)

        basket_text_info += self.__total_basket_cost_text.format(total_cost=self.__total_cost)
        return basket_text_info

    def get_product_showcase_text(self, product_id: int):
        product = self.get_product(product_id)
        basket_text_info = self._product_showcase_template.format(
            product_id=product.id,
            product_name=product.name,
            product_quantity=product.quantity,
            product_cost=product.cost,
            total_cost=product.total_cost
        )
        return basket_text_info

    @classmethod
    def get_empty_basket_case_text(cls):
        return cls.__empty_basket_case_text

    @classmethod
    def get_json_empty_structure(cls):
        return JsonTool.deserialize(JsonTool.serialize(BasketData()))

    @property
    def total_cost(self):
        return self.__total_cost

    def __init__(self, basket_data: BasketData = None):
        super().__init__()
        self.__total_cost: int = 0

        if basket_data is not None:
            self.products = basket_data.transform_to_product_data()
            self.__total_cost = basket_data.total_cost

    def add_product(self, product: Product, quantity: int):
        is_new = True
        product_data = ProductData(
            id=product.id,
            cost=product.cost,
            name=product.name,
            description=product.description,
            picture=product.picture,
            quantity=quantity,
            is_active=product.is_active
        )

        for product_info in self.products:
            if product_info.id == product_data.id:
                existing_product_index = self.products.index(product_info)
                self.products[existing_product_index].quantity += product_data.quantity
                self.products[existing_product_index].total_cost += product_data.total_cost
                self.products[existing_product_index].is_active = product_data.is_active
                is_new = False
                break

        if is_new:
            self.products.append(product_data)
        self.__count_total_cost()

    def delete_product(self, product_id):
        for product in self.products:
            if int(product.id) == int(product_id):
                self.products.remove(product)
                self.__count_total_cost()
                return True
        return False

    def replace_product(self, product_id, new_product: ProductData):
        for product in self.products:
            if int(product.id) == int(product_id):
                self.products[self.products.index(product)] = new_product
        self.__count_total_cost()

    def __count_total_cost(self):
        total_cost = 0
        for product in self.products:
            total_cost += product.total_cost
        self.__total_cost = total_cost

