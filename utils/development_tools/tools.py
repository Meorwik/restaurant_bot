from data.config import CURRENCY_RATIO, CURRENT_CURRENCY
from aiogram import types
from typing import Final
from aiogram import Bot
import json


class MemoryStorage:
    def __repr__(self):
        return "..."

    def s(self):
        ...


class JsonTool:
    @classmethod
    def serialize(cls, obj) -> str:
        """
        Method serializes python object into JSON serializable str object
        :return: JSON serializable str object
        """
        if isinstance(obj, dict):
            return json.dumps(obj, indent=4)
        elif isinstance(obj, str):
            return json.dumps(json.loads(obj))
        else:
            return json.dumps(obj, default=lambda o: o.__dict__, indent=4)

    @classmethod
    def deserialize(cls, json_data: str, object_class=None):
        """
        Method deserializes 'json_data' object into python object
        :return: object
        """
        object_data: dict = json.loads(json_data)
        if object_class is not None:
            return object_class(config=object_data)
        else:
            return object_data


class PaymentsManager:
    __TEST_INVOICE_PAYLOAD: Final[str] = "test-invoice-payload"
    __PROD_INVOICE_PAYLOAD: Final[str] = "XXX"

    def __repr__(self):
        return f"PaymentsManagerObject - {id(self)}"

    def __init__(self, bot: Bot, payment_token: str = None):
        self.__bot: Bot = bot
        self.__config: dict = {
            "currency": CURRENT_CURRENCY,
            "ratio": CURRENCY_RATIO[CURRENT_CURRENCY],
            "token": payment_token,
            "payload": self.__TEST_INVOICE_PAYLOAD
        }

    def set_payment_token(self, payment_token: str):
        self.__config["token"] = payment_token

    def get_currency_ratio(self):
        return self.__config["ratio"]

    async def send_product_invoice(self, chat_id, product, reply_markup=None):
        price = types.LabeledPrice(
            label=product.name,
            amount=self.get_currency_ratio() * product.cost
        )

        return await self.__bot.send_invoice(
            chat_id=chat_id,
            title=product.name,
            description=product.description,
            photo_url=product.picture,
            currency=self.__config["currency"],
            prices=[price],
            provider_token=self.__config["token"],
            payload=self.__config["payload"],
            reply_markup=reply_markup
        )

    async def send_basket_invoice(self, chat_id, basket, reply_markup=None):
        prices = [
            types.LabeledPrice(
                label=product.name,
                amount=product.total_cost * self.get_currency_ratio()
            )
            for product in basket.products
        ]

        description = ""
        for product in basket.products:
            description += f"{product.name} ({product.quantity})-шт | {product.total_cost}\n\n"

        return await self.__bot.send_invoice(
            chat_id=chat_id,
            title="Все товары в вашей корзине",
            description=description,
            currency=self.__config["currency"],
            prices=prices,
            provider_token=self.__config["token"],
            reply_markup=reply_markup,
            payload=self.__config["payload"],
        )


