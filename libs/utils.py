import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Utility functions for handling cookies, local storage, and JSON data
def load_data_from_json(path):
    with open(path, 'r') as file:
        return json.load(file)

def save_data_to_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as file:
        json.dump(data, file)

def add_cookies(driver, cookies):
    for cookie in cookies:
        driver.add_cookie(cookie)

def add_local_storage(driver, local_storage):
    for k, v in local_storage.items():
        driver.execute_script(f"window.localStorage.setItem('{k}', '{v}');")

def wait_for_element(driver, timeout, condition_type, locator_tuple):
    wait = WebDriverWait(driver, timeout)
    return wait.until(condition_type(locator_tuple))
