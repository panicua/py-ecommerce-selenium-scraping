import csv
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from urllib.parse import urljoin

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

# urls for scrapping
BASE_URL = "https://webscraper.io/"
HOME_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/")
COMPUTERS_URL = urljoin(HOME_URL, "computers")
LAPTOPS_URL = urljoin(HOME_URL, "computers/laptops")
TABLETS_URL = urljoin(HOME_URL, "computers/tablets")
PHONES_URL = urljoin(HOME_URL, "phones")
TOUCH_URL = urljoin(HOME_URL, "phones/touch")

# selenium startup options
options = webdriver.ChromeOptions()
options.add_argument("--headless")

# selenium constants
ACCEPT_COOKIES_CLASS = "acceptCookies"
PRODUCT_WRAPPER_CLASS = "product-wrapper"
PRODUCT_TITLE_CLASS = "title"
PRODUCT_DESCRIPTION_CLASS = "description"
PRODUCT_PRICE_CLASS = "price"
PRODUCT_RATING_CLASS = "ws-icon-star"
PRODUCT_REVIEW_COUNT_CLASS = "review-count"
PAGINATION_BUTTON_CLASS = "ecomerce-items-scroll-more"


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


def timer(func: callable) -> callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> callable:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Executed in {elapsed_time: .2f} seconds")
        return result

    return wrapper


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

    @timer
    def parse_page(self, url: str, file_name: str) -> list[Product]:
        self.driver.get(url)

        if not self.cookies_accepted:
            self.check_accept_cookies()

        self.handle_pagination()

        items = self.driver.find_elements(By.CLASS_NAME, PRODUCT_WRAPPER_CLASS)
        list_of_products = []
        for item in items:
            title = item.find_element(
                By.CLASS_NAME, PRODUCT_TITLE_CLASS
            ).get_attribute("title")
            description = item.find_element(
                By.CLASS_NAME, PRODUCT_DESCRIPTION_CLASS
            ).text
            price = float(
                item.find_element(By.CLASS_NAME, PRODUCT_PRICE_CLASS).text[1:]
            )
            rating = len(
                item.find_elements(By.CLASS_NAME, PRODUCT_RATING_CLASS)
            )
            num_of_reviews = int(
                item.find_element(
                    By.CLASS_NAME, PRODUCT_REVIEW_COUNT_CLASS
                ).text.split()[0]
            )
            list_of_products.append(
                Product(title, description, price, rating, num_of_reviews)
            )

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
