import json
import os as _os
import pickle
import time
from pathlib import Path as _Path

from dotenv import load_dotenv as _load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

# Load .env file
_env_path = _Path('.') / '.env'
_load_dotenv(dotenv_path=_env_path)

_cookie_path = _Path("./api/wrapper/browser/.cookies.pkl")

# Retrieve Unifi cloud address
_UNIFI_ADDRESS = _os.getenv("UNIFI_ADDRESS")

# Retrieve the credentials
_UNIFI_USER = _os.getenv("UNIFI_USER")
_UNIFI_PASSWORD = _os.getenv("UNIFI_PASSWORD")


class AutomatedWebDriver():
    def __init__(self, url: str, run_headless: bool = True, explicit_wait_time: int = 60, implicit_wait_time: int = 10):
        """Initializes the web driver class to make requests to the Ubiquiti cloud frontend
        
        Arguments:
            url {str} -- url to visit
        
        Keyword Arguments:
            run_headless {bool} -- Sets whether the browser should run headlessly (default: True)
            explicit_wait_time {int} -- wait maximum of X time for condition to be true, this is used to find 
            certain elements that might take a long time to load (default: {60})
            implicit_wait_time {int} -- wait maximum of X time for an element to be found (default: {10})
        """
        self.options = Options()
        self.options.headless = run_headless
        self.driver = webdriver.Firefox(options=self.options, executable_path=_os.getcwd(
        ) + '/api/bin/geckodriver', service_log_path='/tmp/geckodriver.log')
        self.wait = WebDriverWait(self.driver, explicit_wait_time)
        self.url = url
        self.driver.implicitly_wait(implicit_wait_time)

    def get_clients(self):
        """Retrieves the number of clients
        """
        self.driver.get(self.url)
        if _cookie_path.exists():
            try:
                # Load in the cookies
                cookies = pickle.load(open(_cookie_path, "rb"))
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                # Refresh the page so that the site gets loaded with the added cookies
                self.driver.refresh()
            except:
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
            except:
                raise

        try:
            self.wait.until(EC.title_contains("UniFi Cloud Access Portal"))
            # stop the execution of the program so that the cloud interface can load the values
            time.sleep(10)

            pickle.dump(self.driver.get_cookies(), open(
                _cookie_path, "wb"))  # dump the new cookies

            incentro_element_clients = self.driver.find_element_by_xpath(
                "//td[@class='controllerClients visible--mdUp ng-binding']").text
            self.driver.quit()
            return(incentro_element_clients)
        except:
            raise