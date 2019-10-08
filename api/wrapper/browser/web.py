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

# Load .env file
env_path = _Path('.') / '.env'
_load_dotenv(dotenv_path=env_path)

UNIFI_USER = _os.getenv("UNIFI_USER")
UNIFI_PASSWORD = _os.getenv("UNIFI_PASSWORD")
cookie_path = _Path("./api/wrapper/browser/.cookies.pkl")

driver = webdriver.Firefox(
    executable_path=_os.getcwd() + '/api/bin/geckodriver')
wait = WebDriverWait(driver, 120)
# TODO: remove credentials
# UNIFI_USER = "ch14346"
# UNIFI_PASSWORD = "exZu54rMe6JV7M4Qv0EF"
driver.implicitly_wait(10)
driver.get("https://unifi.ui.com")
if cookie_path.exists():
    try:
        cookies = pickle.load(open(cookie_path, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
    except:
        raise
else:
    wait.until(EC.title_contains("Ubiquiti Account"))

    username_field = driver.find_element_by_name("username")
    username_field.click()
    username_field.send_keys(UNIFI_USER)

    password_field = driver.find_element_by_name("password")
    password_field.click()
    password_field.send_keys(UNIFI_PASSWORD)

    # Find login button
    button = driver.find_element_by_xpath('//button[@class="css-1hho3xm"]')
    button.click()

    # Time to solve captcha

    wait.until(EC.title_contains("UniFi Cloud Access Portal"))

    pickle.dump(driver.get_cookies(), open(cookie_path, "wb"))

wait.until(EC.title_contains("UniFi Cloud Access Portal"))
# sleep the program so that the cloud interface can load the values
time.sleep(10)

pickle.dump(driver.get_cookies(), open(
    cookie_path, "wb"))  # dump the new cookies

incentro_element_table = driver.find_element_by_xpath(
    "//body//tbody//tr[1]").text
# print("Incentro element table is")
print(incentro_element_table)

incentro_element_clients = driver.find_element_by_xpath(
    "//td[@class='controllerClients visible--mdUp ng-binding']").text
# print("Incentro clients are")
print(incentro_element_clients)


class AutomatedWebDriver():
    def __init__(self, wait_timeout: int, url: str):
        self.driver = webdriver.Firefox(
            executable_path=_os.getcwd() + '/api/bin/geckodriver')
        self.wait = WebDriverWait(self.driver, wait_timeout)
        self.url = url
