from utils.development_tools.tools import JsonTool
from core.market import Category, Product, Basket, BasketData
from utils.misc.logging import DATABASE_LOGGER
from aiogram.types import User
import asyncpg

DEFAULT_ROLE = "user"


class DataBaseManager:
    def __init__(self, config):
        self.config = config
        self.pool = None

    async def init_pool(self):
        self.pool: asyncpg.Pool = await asyncpg.create_pool(self.config)
        if bool(self.pool):
            DATABASE_LOGGER.info(msg="DATABASE: pool started")


class PostgresDataBaseManager(DataBaseManager):
    async def get_last_value_data(self, table_name: str) -> int:
        """
        Method returns last value sequence from specified table
        :param table_name:
        :return: <Record lastval>
        """

        id_seq_sql = f"SELECT LASTVAL() FROM {table_name};"

        id_seq = await self.pool.fetchrow(id_seq_sql)
        id_seq = int(id_seq.get('lastval'))
        return id_seq

    """
    ------------------------CREATING TABLES SECTION OPEN--------------------------
    """

    async def create_user_baskets_table(self):
        create_user_baskets_table_sql = """
        CREATE TABLE IF NOT EXISTS baskets(
        "id" serial PRIMARY KEY,
        "user_id" INTEGER UNIQUE NOT NULL,
        "basket_info" JSONB 
        );
        """
        await self.pool.execute(create_user_baskets_table_sql)
        return True

    async def create_users_table(self):
        users_table_sql = f"""
        CREATE TABLE IF NOT EXISTS users(
        "id" serial PRIMARY KEY,
        "user_id" VARCHAR (50) UNIQUE NOT NULL,
        "username" VARCHAR (50),
        "first_name" VARCHAR (50),
        "last_name" VARCHAR (50),
        "role" VARCHAR(50) NOT NULL DEFAULT '{DEFAULT_ROLE}',
        "register_date" DATE NOT NULL DEFAULT CURRENT_DATE);
        """
        await self.pool.execute(users_table_sql)
        return True

    async def create_categories_table(self):
        categories_table_sql = """
        CREATE TABLE IF NOT EXISTS categories(
        "id" serial PRIMARY KEY,
        "name" VARCHAR(50) NOT NULL,
        "picture_url" TEXT);
        """
        await self.pool.execute(categories_table_sql)
        return True

    async def create_products_table(self):
        products_table_sql = """
        CREATE TABLE IF NOT EXISTS products(
        "id" serial PRIMARY KEY,
        "category_id" INTEGER NOT NULL,
        "name" VARCHAR(50) NOT NULL,
        "cost" VARCHAR(50) NOT NULL,
        "description" TEXT,
        "picture_url" TEXT,
        "quantity_on_stock" VARCHAR(35),
        FOREIGN KEY (category_id) REFERENCES categories(id));
        """
        await self.pool.execute(products_table_sql)
        return True

    """
    ------------------------CREATING TABLES SECTION CLOSE--------------------------
    
    
    
    ------------------------USERS TABLE METHODS SECTION OPEN--------------------------
    """

    async def add_user(self, user: User) -> int:
        """
        Method 'add_user' :returns the last id sequence where user was inserted
        :param user: User
        :return: int
        """
        add_new_user_sql = f"""
        INSERT INTO users (user_id, username, first_name, last_name) 
        VALUES ('{user.id}', '{user.username}', '{user.first_name}', '{user.last_name}');
        """
        await self.pool.execute(add_new_user_sql)

        return await self.get_last_value_data("users")

    async def get_user_id(self, user_id) -> int:
        get_user_id_sql = f"""
        SELECT id FROM users WHERE user_id = '{user_id}'
        """
        result = await self.pool.fetchrow(get_user_id_sql)
        return int(result.get("id"))

    async def is_new_user(self, user: User) -> bool:
        get_user_sql = f"""
        SELECT user_id FROM users WHERE user_id = '{user.id}'
        """
        result = await self.pool.fetch(get_user_sql)
        return not result

    async def is_admin(self, user: User) -> bool:
        is_admin_sql = f"""
        SELECT user_id FROM users WHERE role = 'admin' AND user_id = '{user.id}'
        """
        result = await self.pool.fetch(is_admin_sql)
        return bool(result)

    """
    ------------------------USERS TABLE METHODS SECTION CLOSE--------------------------
    
    
    ---------------CATEGORIES AND PRODUCTS TABLE METHODS SECTION OPEN------------------
    """

    async def get_product_list_from_category(self, category_id: int) -> list:
        get_category_products_sql = f"""
        SELECT * FROM products WHERE category_id = {category_id}
        """
        fetch_result = await self.pool.fetch(get_category_products_sql)
        category_products = [
            Product(
                product_id=product.get("id"),
                name=product.get("name"),
                cost=product.get("cost"),
                description=product.get("description"),
                product_picture=product.get("picture_url")
            )
            for product in fetch_result
        ]

        return category_products

    async def get_categories_list(self) -> list:
        get_category_list_sql = """
        SELECT * FROM categories
        """
        fetch_result = await self.pool.fetch(get_category_list_sql)
        categories = [
            Category(category_id=category.get("id"), name=category.get("name"), picture_url=category.get("picture_url"))
            for category in fetch_result
        ]

        return categories

    async def get_category_with_products(self, category_id: int) -> Category:
        get_category_sql = f"""
        SELECT * FROM categories WHERE id = {category_id}
        """
        category_data = await self.pool.fetchrow(get_category_sql)
        category_to_return = Category(
            category_id=int(category_data.get("id")),
            name=category_data.get("name"),
            picture_url=category_data.get("picture_url")
        )

        category_products = await self.get_product_list_from_category(category_id)

        for product in category_products:
            category_to_return.add_product(product)

        return category_to_return

    async def is_available_product(self, product_id: str) -> bool:
        is_available_product_sql = f"""
        SELECT is_active FROM products WHERE id = '{product_id}'
        """

        result = await self.pool.fetch(is_available_product_sql)
        return result[0].get('is_active')

    async def update_product_status(self, product_id, status: bool):
        update_product_status_sql = f"""
        UPDATE products SET is_active = '{status}' WHERE id = {product_id}
        """

        await self.pool.execute(update_product_status_sql)

    """
    ---------------CATEGORIES AND PRODUCTS TABLE METHODS SECTION CLOSE------------------
    
    
    ------------------------BASKET TABLE METHODS SECTION OPEN----------------------------
    """

    async def create_new_basket(self, user_id: int):
        empty_json = JsonTool.serialize(Basket.get_json_empty_structure())
        create_new_basket_sql = f"""
        INSERT INTO baskets (user_id, basket_info) VALUES ({user_id}, '{empty_json}')
        """
        await self.pool.execute(create_new_basket_sql)

    async def get_user_basket(self, user_id: int) -> Basket:
        get_user_basket_info_sql = f"""
        SELECT basket_info FROM baskets WHERE user_id = {user_id}
        """
        result = await self.pool.fetchrow(get_user_basket_info_sql)
        if result:
            basket_info = JsonTool.deserialize(result.get("basket_info"))
            basket_data_object = BasketData(
                products=basket_info["products"],
                total_cost=basket_info["total_cost"]
            )
            return Basket(basket_data_object)

        else:
            raise Exception("INVALID USER ID - NO SUCH BASKET")

    async def update_user_basket(self, basket: Basket, user_id: int):
        basket_data = BasketData(
            products=basket.products,
            total_cost=basket.total_cost
        )
        basket = JsonTool.serialize(basket_data)
        update_user_basket_sql = f"""
        UPDATE baskets SET basket_info = '{basket}' WHERE user_id = '{user_id}'
        """
        await self.pool.execute(update_user_basket_sql)

    async def clear_basket(self, user_id: int):
        empty_json = JsonTool.serialize(Basket.get_json_empty_structure())
        clear_basket_sql = f"""
        UPDATE baskets SET basket_info = '{empty_json}' WHERE user_id = '{user_id}'
        """
        await self.pool.execute(clear_basket_sql)

