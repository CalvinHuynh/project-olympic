import json
import os
import pickle
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

firefox_executable_path = {
    'executable_path': os.getcwd() + '/api/bin/geckodriver'}
driver = webdriver.Firefox(
    executable_path=os.getcwd() + '/api/bin/geckodriver')
wait = WebDriverWait(driver, 120)
# TODO: remove credentials
UNIFI_USER = ""
UNIFI_PASSWORD = ""

driver.implicitly_wait(10)
driver.get("https://unifi.ui.com")
cookies_file = Path(".cookies.pkl")
if cookies_file.exists():
    try:
        cookies = pickle.load(open(".cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
    except:
        pass
wait.until(EC.title_contains("Ubiquiti Account"))
assert "Ubiquiti" in driver.title

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

pickle.dump(driver.get_cookies(), open(".cookies.pkl", "wb"))

# incentro_element = driver.find_element_by_xpath("//span[text()='Incentro AMS Olympic']")
table_row = driver.find_element_by_xpath(
    "//table[@class='ng-scope ng-isolate-scope clickable']/tbody/tr")
print(table_row)
