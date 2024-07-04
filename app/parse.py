import csv
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from tqdm import tqdm

from app.constants import (
    ACCEPT_COOKIES_CLASS,
    PRODUCT_WRAPPER_CLASS,
    PRODUCT_TITLE_CLASS,
    PRODUCT_DESCRIPTION_CLASS,
    PRODUCT_PRICE_CLASS,
    PRODUCT_RATING_CLASS,
    PRODUCT_REVIEW_COUNT_CLASS,
    PAGINATION_BUTTON_CLASS,
    HOME_URL,
    COMPUTERS_URL,
    LAPTOPS_URL,
    TABLETS_URL,
    PHONES_URL,
    TOUCH_URL,
)

# selenium startup options
options = webdriver.ChromeOptions()
options.add_argument("--headless")


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int


class AbstractParser(ABC):
    @abstractmethod
    def parse_page(self, url: str, file_name: str) -> list[Product]:
        pass


def create_csv_file(file_name: str, list_of_products: list[Product]) -> None:
    """
    Creates csv file with list of products and its attributes
    """
    with open(file_name, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["title", "description", "price", "rating", "num_of_reviews"]
        )
        for product in list_of_products:
            writer.writerow(
                [
                    product.title,
                    product.description,
                    product.price,
                    product.rating,
                    product.num_of_reviews,
                ]
            )


class ElectronicProductParser(AbstractParser):
    def __init__(self, driver: webdriver.Chrome) -> None:
        self.driver = driver
        self.cookies_accepted = False

    def parse_page(self, url: str, file_name: str) -> list[Product]:
        self.driver.get(url)

        if not self.cookies_accepted:
            self.check_accept_cookies()

        self.handle_pagination()

        items = self.driver.find_elements(By.CLASS_NAME, PRODUCT_WRAPPER_CLASS)
        list_of_products = []

        # tqdm for progress tracking visualization
        with tqdm(
                total=len(items), desc="Parsing Products", unit_scale=True
        ) as pbar:
            for item in items:
                title = self.get_title(item)
                description = self.get_description(item)
                price = self.get_price(item)
                rating = self.get_rating(item)
                num_of_reviews = self.get_num_of_reviews(item)
                list_of_products.append(
                    Product(title, description, price, rating, num_of_reviews)
                )

                pbar.update(1)

        create_csv_file(file_name, list_of_products)
        return list_of_products

    def check_accept_cookies(self) -> None:
        """
        Check if cookies are accepted, if not click on accept button
        """
        try:
            cookies_accept = self.driver.find_element(
                By.CLASS_NAME, ACCEPT_COOKIES_CLASS
            )
            cookies_accept.click()
        except NoSuchElementException:
            print("Cookies were already accepted (accept button not found)")
        self.cookies_accepted = True

    def handle_pagination(self) -> None:
        """
        Handle pagination if it exists, click on it and wait for it to load
        else do nothing
        """
        while True:
            try:
                pagination_button = self.driver.find_element(
                    By.CLASS_NAME, PAGINATION_BUTTON_CLASS
                )
                if pagination_button.is_displayed():
                    pagination_button.click()
                    time.sleep(0.1)
                else:
                    break
            except NoSuchElementException:
                break
        time.sleep(1)

    @staticmethod
    def get_title(item: WebElement) -> str:
        return item.find_element(
            By.CLASS_NAME, PRODUCT_TITLE_CLASS
        ).get_attribute("title")

    @staticmethod
    def get_description(item: WebElement) -> str:
        return item.find_element(
            By.CLASS_NAME, PRODUCT_DESCRIPTION_CLASS
        ).text

    @staticmethod
    def get_price(item: WebElement) -> float:
        return float(
            item.find_element(By.CLASS_NAME, PRODUCT_PRICE_CLASS).text[1:]
        )

    @staticmethod
    def get_rating(item: WebElement) -> int:
        return len(
            item.find_elements(By.CLASS_NAME, PRODUCT_RATING_CLASS)
        )

    @staticmethod
    def get_num_of_reviews(item: WebElement) -> int:
        return int(
            item.find_element(
                By.CLASS_NAME, PRODUCT_REVIEW_COUNT_CLASS
            ).text.split()[0]
        )


def get_all_products() -> None:
    with webdriver.Chrome(options=options) as driver:
        parser = ElectronicProductParser(driver)
        for category, url, file_name in [
            ("Home products", HOME_URL, "home.csv"),
            ("Computer products", COMPUTERS_URL, "computers.csv"),
            ("Laptop products", LAPTOPS_URL, "laptops.csv"),
            ("Tablet products", TABLETS_URL, "tablets.csv"),
            ("Phone products", PHONES_URL, "phones.csv"),
            ("Touch products", TOUCH_URL, "touch.csv"),
        ]:
            print(category)
            parser.parse_page(url, file_name)


if __name__ == "__main__":
    get_all_products()
