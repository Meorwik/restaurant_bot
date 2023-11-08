from aiogram.types import InputMediaPhoto


class Category:
    def __repr__(self):
        return f"CategoryObject: {self._name}"

    def __init__(self,  category_id: int, name: str, picture_url=None):
        self.__id = category_id
        self._name = name
        self.__products = {}

        if picture_url is not None:
            self.__picture = InputMediaPhoto(picture_url)
        else:
            self.__picture = None

    def get_id(self):
        return self.__id

    def add_product(self, product):
        self.__products[f"{product.get_id()}"] = product

    def get_name(self):
        return self._name

    def get_products(self):
        return self.__products

    def get_product_ids(self):
        ids = [str(key) for key in self.__products.keys()]
        return ids

    def get_product(self, product_id):
        if product_id in self.__products.keys():
            return self.__products[f"{product_id}"]

    def get_picture(self):
        return self.__picture


class Product:
    def __init__(self, product_id=None, cost=None, name=None, description=None, product_picture=None):
        self.__id = product_id
        self.__cost = cost
        self.__name = name
        self.__description = description
        self.__product_picture = product_picture

    def get_id(self):
        return self.__id

    def get_cost(self):
        return self.__cost

    def get_name(self):
        return self.__name

    def get_description(self):
        return self.__description

    def get_picture(self):
        return self.__product_picture


class Basket:
    def __init__(self):
        self.__products: list = []

    def add_product(self, product: Product):
        self.__products.append(product)

    def delete_product(self):
        ...


