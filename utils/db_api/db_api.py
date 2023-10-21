from core.market import Category, Product
from aiogram.types import User
from datetime import date
import asyncpg

DEFAULT_ROLE = "user"

class DataBaseManager:
    def __init__(self, config):
        self.config = config
        self.connection: asyncpg.Connection = None

    async def set_connection(self):
        if self.connection is None or self.connection.is_closed():
            self.connection = await asyncpg.connect(self.config)
        return self.connection

    async def close_connection(self):
        await self.connection.close()


class PostgresDataBaseManager(DataBaseManager):
    async def create_users_table(self):
        today = date.today()
        users_table_sql = f"""
        CREATE TABLE IF NOT EXISTS users(
        "id" serial PRIMARY KEY,
        "user_id" VARCHAR (50) UNIQUE NOT NULL,
        "username" VARCHAR (50),
        "first_name" VARCHAR (50),
        "last_name" VARCHAR (50),
        "role" VARCHAR(50) NOT NULL DEFAULT '{DEFAULT_ROLE}',
        "register_date" DATE NOT NULL DEFAULT '{today}');
        """
        await self.connection.execute(users_table_sql)

    async def create_categories_table(self):
        categories_table_sql = """
        CREATE TABLE IF NOT EXISTS categories(
        "id" serial PRIMARY KEY,
        "name" VARCHAR(50) NOT NULL,
        "picture_url" TEXT);
        """
        await self.connection.execute(categories_table_sql)

    async def create_products_table(self):
        products_table_sql = """
        CREATE TABLE IF NOT EXISTS products(
        "id" serial PRIMARY KEY,
        "category_id" INTEGER NOT NULL,
        "name" VARCHAR(50) NOT NULL,
        "cost" VARCHAR(50) NOT NULL,
        "description" TEXT,
        "picture_url" TEXT,
        FOREIGN KEY (category_id) REFERENCES categories(id));
        """
        await self.connection.execute(products_table_sql)

    async def add_user(self, user: User):
        add_new_user_sql = f"""
        INSERT INTO users (user_id, username, first_name, last_name) 
        VALUES ('{user.id}', '{user.username}', '{user.first_name}', '{user.last_name}')
        """
        await self.connection.execute(add_new_user_sql)

    async def is_new_user(self, user: User) -> bool:
        get_user_sql = f"""
        SELECT user_id FROM users WHERE user_id = '{user.id}'
        """
        result = await self.connection.fetch(get_user_sql)
        return not result

    async def is_admin(self, user: User) -> bool:
        is_admin_sql = f"""
        SELECT user_id FROM users WHERE role = 'admin' AND user_id = '{user.id}'
        """
        result = await self.connection.fetch(is_admin_sql)
        return bool(result)

    async def get_categories_count(self) -> int:
        get_categories_count_sql = """
        SELECT COUNT(id) FROM categories
        """
        result: asyncpg.Record = await self.connection.fetchrow(
            get_categories_count_sql
        )
        count = int(result.get("count"))
        return count

    async def get_product_list_from_category(self, category_id: int) -> list:
        get_category_products_sql = f"""
        SELECT * FROM products WHERE category_id = {category_id}
        """
        fetch_result = await self.connection.fetch(get_category_products_sql)
        category_products = [
            Product(
                product_id=product.get("id"),
                name=product.get("name"),
                cost=product.get("cost"),
                description=product.get("description"),
                product_picture=product.get("product_picture")
            )
            for product in fetch_result
        ]

        return category_products

    async def get_categories_list(self) -> list:
        get_category_list_sql = """
        SELECT * FROM categories
        """
        fetch_result = await self.connection.fetch(get_category_list_sql)
        categories = [
            Category(category_id=category.get("id"), name=category.get("name"), picture_url=category.get("picture_url"))
            for category in fetch_result
        ]

        return categories

    async def get_category_with_products(self, category_id: int) -> Category:
        get_category_sql = f"""
        SELECT * FROM categories WHERE id = {category_id}
        """
        category_data = await self.connection.fetchrow(get_category_sql)
        category_to_return = Category(
            category_id=int(category_data.get("id")),
            name=category_data.get("name")
        )

        category_products = await self.get_product_list_from_category(category_id)

        for product in category_products:
            category_to_return.add_product(product)

        return category_to_return

    async def get_product(self, product_id: int) -> Product:
        get_product_sql = f"""
        SELECT * FROM products WHERE id = {product_id}
        """
        product_info = await self.connection.fetchrow(get_product_sql)
        product = Product(
            product_id=int(product_info.get("id")),
            name=product_info.get("name"),
            cost=product_info.get("cost"),
            description=product_info.get("description"),
            product_picture=product_info.get("picture_url")
        )

        return product

    async def get_products_count_in_category(self, category_id: int) -> int:
        get_products_count_in_category_sql = f"""
        SELECT COUNT(id) FROM products WHERE category_id = {category_id}
        """
        database_record = await self.connection.fetchrow(get_products_count_in_category_sql)
        count = int(database_record.get("count"))
        return count

