from urllib.parse import urljoin


# urls for scrapping
BASE_URL = "https://webscraper.io/"
HOME_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/")
COMPUTERS_URL = urljoin(HOME_URL, "computers")
LAPTOPS_URL = urljoin(HOME_URL, "computers/laptops")
TABLETS_URL = urljoin(HOME_URL, "computers/tablets")
PHONES_URL = urljoin(HOME_URL, "phones")
TOUCH_URL = urljoin(HOME_URL, "phones/touch")

# selenium constants
ACCEPT_COOKIES_CLASS = "acceptCookies"
PRODUCT_WRAPPER_CLASS = "product-wrapper"
PRODUCT_TITLE_CLASS = "title"
PRODUCT_DESCRIPTION_CLASS = "description"
PRODUCT_PRICE_CLASS = "price"
PRODUCT_RATING_CLASS = "ws-icon-star"
PRODUCT_REVIEW_COUNT_CLASS = "review-count"
PAGINATION_BUTTON_CLASS = "ecomerce-items-scroll-more"
