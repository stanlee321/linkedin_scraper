import json
import os
import string
import random
import urllib.parse

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



def generate_linkedin_search_url(geo_urns, industries, keywords, profile_language, page, sid):
    # search_url = f"https://www.linkedin.com/search/results/people/?keywords={pattern}&origin=GLOBAL_SEARCH_HEADER&page={page}&sid={randomseed}"

    base_url = "https://www.linkedin.com/search/results/people/"
    
    # Convert lists to JSON-like array strings and encode
    geo_urn_param = urllib.parse.quote(str(geo_urns).replace("'", '"'))
    industry_param = urllib.parse.quote(str(industries).replace("'", '"'))
    keywords_param = urllib.parse.quote(keywords)
    profile_language_param = urllib.parse.quote(str(profile_language).replace("'", '"'))
    
    # Construct the full URL with all parameters
    url = (f"{base_url}?geoUrn={geo_urn_param}&industry={industry_param}&"
           f"keywords={keywords_param}&origin=FACETED_SEARCH&"
           f"page={page}&"
           f"profileLanguage={profile_language_param}&sid={sid}")
    
    return url

def generate_random_string():
    """
    Generates a random string of 3 letters.
    
    Returns:
        str: A random string of 3 letters.
    """
    letters = string.ascii_letters  # Get all letters (uppercase and lowercase)
    random_string = ''.join(random.choices(letters, k=3))
    return random_string

# Example usage
geo_urns = ["104379274"]
industries = ["2358","14","4","43"]
keywords = "c# developer"
profile_language = ["es"]
sid = "QjK"
page =2 

url = generate_linkedin_search_url(geo_urns, industries, keywords, profile_language,page, sid)
print(url)


