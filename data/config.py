import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")

PAYMENT_TOKEN = os.environ.get("ROBOKASSA_TOKEN")


CURRENCY_RATIO = {
    "RUB": 100,
    "KZT": 100
}

CURRENT_CURRENCY = os.environ.get("CURRENT_CURRENCY")
