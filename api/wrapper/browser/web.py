import os as _os
import pickle
import time
from enum import Enum
from pathlib import Path as _Path

from dotenv import load_dotenv as _load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as _ChromeOptions
from selenium.webdriver.firefox.options import Options as _FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Load .env file
_env_path = _Path('.') / '.env'
_load_dotenv(dotenv_path=_env_path)

_cookie_path = _os.path.join(_os.path.abspath(_os.path.dirname(__file__)),
                             '.cookies.pkl')

# Retrieve Unifi cloud address
_UNIFI_ADDRESS = _os.getenv("UNIFI_ADDRESS")

# Retrieve the credentials
_UNIFI_USER = _os.getenv("UNIFI_USER")
_UNIFI_PASSWORD = _os.getenv("UNIFI_PASSWORD")


class WebDriverType(Enum):
    """
    The types of currently supported web drivers
    """

    # Returns the value of the enum

    def __str__(self):
        return str(self.value)

    CHROME = 'chromedriver'
    FIREFOX = 'geckodriver'


def _get_driver_path(driver_name: str):
    return str((_Path(__file__).parent / f'../../bin/{driver_name}').resolve())


def _initialize_driver(driver_name: WebDriverType,
                       path_to_executable: str = None,
                       run_headless: bool = True):
    if driver_name == WebDriverType.CHROME:
        _driver_path = _get_driver_path(driver_name)
        _options = _ChromeOptions()
        _options.headless = run_headless
        _options.add_argument("--no-sandbox")
        _options.add_argument("--window-size=1920,1080")
        _options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=_options,
                                  executable_path=_driver_path,
                                  service_log_path=f'/tmp/{driver_name}.log')
        return driver
    elif driver_name == WebDriverType.FIREFOX:
        _driver_path = _get_driver_path(driver_name)
        _options = _FirefoxOptions()
        _options.headless = run_headless
        driver = webdriver.Firefox(options=_options,
                                   executable_path=_driver_path,
                                   service_log_path=f'/tmp/{driver_name}.log')
        return driver
    else:
        raise ValueError('driver_name is required')


class AutomatedWebDriver():
    def __init__(self,
                 url: str,
                 driver_name: WebDriverType,
                 run_headless: bool = True,
                 explicit_wait_time: int = 60,
                 implicit_wait_time: int = 10):
        """
        Initializes the web driver class to make requests to the Ubiquiti
        cloud frontend

        Arguments:
            url {str} -- url to visit
            driver_name {WebDriverType} -- type of web driver to use
            (currently supports firefox and chrome)

        Keyword Arguments:
            run_headless {bool} -- Sets whether the browser should run
            headlessly (default: True)
            explicit_wait_time {int} -- wait maximum of X time for condition
            to be true, this is used to find certain elements that might take
            a long time to load (default: {60})
            implicit_wait_time {int} -- wait maximum of X time for an element
            to be found (default: {10})
        """
        self.driver = _initialize_driver(driver_name,
                                         run_headless=run_headless)
        self.wait = WebDriverWait(self.driver, explicit_wait_time)
        self.url = url
        self.driver.implicitly_wait(implicit_wait_time)

    def get_clients(self):
        """Retrieves the number of clients
        """
        self.driver.get(self.url)
        if _os.path.isfile(_cookie_path):
            try:
                # Load in the cookies
                cookies = pickle.load(open(_cookie_path, "rb"))
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                # Refresh the page so that the site gets loaded with
                # the added cookies
                self.driver.refresh()
            except BaseException:
                raise
        else:
            try:
                self.wait.until(EC.title_contains("Ubiquiti Account"))

                username_field = self.driver.find_element_by_name("username")
                username_field.click()
                username_field.send_keys(_UNIFI_USER)

                password_field = self.driver.find_element_by_name("password")
                password_field.click()
                password_field.send_keys(_UNIFI_PASSWORD)

                # Find login button
                button = self.driver.find_element_by_xpath(
                    '//button[@class="css-1hho3xm"]')
                button.click()

                # Wait for the user to solve the captcha
                self.wait.until(EC.title_contains("UniFi Cloud Access Portal"))

                pickle.dump(self.driver.get_cookies(),
                            open(_cookie_path, "wb"))
            except BaseException:
                raise

        try:
            self.wait.until(EC.title_contains("UniFi Cloud Access Portal"))
            # stop the execution of the program so that the cloud
            # interface can load the values
            time.sleep(10)

            pickle.dump(self.driver.get_cookies(),
                        open(_cookie_path, "wb"))  # dump the new cookies

            number_of_clients = self.driver.find_element_by_xpath(
                "//td[@class='controllerClients visible--mdUp ng-binding']"
            ).text
            self.driver.quit()
            return (number_of_clients)
        except BaseException:
            raise
