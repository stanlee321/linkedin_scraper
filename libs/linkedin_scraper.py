from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import json
import os
import string
import random
# from libs.settings import CONFIG
from libs.utils import load_data_from_json, save_data_to_json, add_cookies, add_local_storage, wait_for_element

from typing import List

class LinkedInScraper:
    def __init__(self, save_json=True,):
        
        self.folders = ["./outputs", "./auth"]
        
        for folder in self.folders:
            self.create_folder(folder)
        
        self.login_url = "https://www.linkedin.com/login"
        self.user_agent = "My Standard Browser and Standard Device"
        self.cookie_path =  f"{self.folders[1]}/cookies.json"
        self.local_storage_path = f"{self.folders[1]}/local_storage.json"
        
        
        self.driver = self.initialize_driver()
        self.action = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, 20)
        self.save_json = save_json

        
    def initialize_driver(self):
        options = webdriver.EdgeOptions()
        options.use_chromium = True
        options.add_argument("start-maximized")
        options.page_load_strategy = 'eager'
        options.add_argument(f"user-agent={self.user_agent}")
        options.add_experimental_option("detach", True)
        return webdriver.Edge(options=options)

    def load_cookies_and_local_storage(self):
        print("self.cookie_path", self.cookie_path)
        print("self.local_storage_path", self.local_storage_path)
        if os.path.exists(self.cookie_path) and os.path.exists(self.local_storage_path):
            cookies = load_data_from_json(self.cookie_path)
            local_storage = load_data_from_json(self.local_storage_path)
            add_cookies(self.driver, cookies)
            add_local_storage(self.driver, local_storage)
            return True
        return False

    def login(self, username: str, password: str):
        
        print(f"Login with usename {username} and pass {password}")
        self.driver.get(self.login_url)
        time.sleep(3)  # Wait for the page to load
        local_exists = self.load_cookies_and_local_storage()
        
        print("local_exists: ", local_exists)
        if not local_exists:
            print("load_cookies_and_local_storage does not existss...", )
            self.wait.until(EC.element_to_be_clickable((By.ID, "username"))).send_keys(username)
            self.wait.until(EC.element_to_be_clickable((By.ID, "password"))).send_keys(password)
            self.action.click(self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Sign in")]')))).perform()
            time.sleep(15)  # Wait for potential redirects and page loads

            print("Saving local data...")
            # Save cookies and local storage after successful login
            save_data_to_json(self.driver.get_cookies(), self.cookie_path)
            save_data_to_json({key: self.driver.execute_script(f"return window.localStorage.getItem('{key}');")
                               for key in self.driver.execute_script("return Object.keys(window.localStorage);")}, self.local_storage_path)



    def extract_data(self, driver : webdriver.Edge, el: int) -> list:
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        # If all is ok, get the HTML data from the page from the full XPATH using BS4

        def get_url(el):
            fullpath = f'html > body > div:nth-of-type({el}) > div:nth-of-type(3) > div:nth-of-type(2) > div > div:first-of-type > main'
            return fullpath
        
        fullpath = get_url(el)
        element = soup.select_one(fullpath)
        if element is None:
            print(f"Element with full path '{fullpath}' not found")
            return []
        # New code to get all 'li' elements inside 'element'
        li_elements = element.select('li')

        return li_elements
    
    def clean_profile_url(self, url: str) -> str:
        # Define the regex pattern to capture everything before the '?'
        pattern = re.compile(r'(https://www\.linkedin\.com/in/[^?]+)')
        # Search for the pattern in the input URL
        match = pattern.search(url)
        # If a match is found, return the cleaned URL, otherwise return the original URL
        return match.group(1) if match else url
    
    @staticmethod
    def create_folder(relative_path: str):
        """
        Creates a folder from a given relative path.

        Args:
            relative_path (str): The relative path of the folder to be created.
        """
        try:
            os.makedirs(relative_path, exist_ok=True)
            print(f"Folder '{relative_path}' created successfully.")
        except OSError as e:
            print(f"Error creating folder '{relative_path}': {e}")
        
    @staticmethod
    def load_json_files(directory: str):
        """
        Loads JSON files from a directory and returns a list of dictionaries.

        Args:
            directory (str): The path to the directory containing the JSON files.

        Returns:
            list: A list of dictionaries loaded from the JSON files.
        """
        data = []
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                with open(file_path, 'r') as file:
                    json_data = json.load(file)
                    data.append(json_data)
        return data

    def search_and_extract(self, pattern, page_start, page_end, debug:bool = False)-> List[dict]:
        
        data = []
        
        if debug:
            data = LinkedInScraper.load_json_files(self.folders[0])
        else:
            
            for page in range(page_start, page_end + 1):
                
                def generate_random_string():
                    """
                    Generates a random string of 3 letters.
                    
                    Returns:
                        str: A random string of 3 letters.
                    """
                    letters = string.ascii_letters  # Get all letters (uppercase and lowercase)
                    random_string = ''.join(random.choices(letters, k=3))
                    return random_string

                randomseed = generate_random_string()
                
                pattern = pattern.replace(' ', '%20')
                pattern = pattern.replace("#", "%23")
                
                search_url = f"https://www.linkedin.com/search/results/people/?keywords={pattern}&origin=GLOBAL_SEARCH_HEADER&page={page}&sid={randomseed}"
                print("search url")
                print(search_url)
                self.driver.get(search_url)
                time.sleep(5)  # Adjust based on your connection speed

                li_elements = self.extract_data(self.driver, 5)
                if len(li_elements)  == 0:
                    li_elements = self.extract_data(self.driver, 4)
                    if len(li_elements) == 0:
                        continue
                
                # Extract information from the page
                profiles = self.extract_information(li_elements, page)

                # Save data
                if self.save_json:
                    self.save_extracted_data(profiles, page)
                data.append(profiles)
            
        print("Done!")
        return data
    
    def extract_information(self, li_elements : List[BeautifulSoup], page: int) -> dict:

        profiles = {
            "page": page,
            "data": []
        }
        
        for soup in li_elements:
            
            # Initialize a dictionary to store the extracted information
            profile_info = {
                'name': '',
                'role': '',
                'location': '',
                'connection': '',
                'services': '',
                'profile_url': ''  # Added field for the profile URL
            }
            
            # Extract the name
            name_tag = soup.find('img', {'class': 'presence-entity__image'})
            if name_tag and name_tag.has_attr('alt'):
                profile_info['name'] = name_tag['alt']
            
            # Extract the role
            role_tag = soup.find('div', {'class': 'entity-result__primary-subtitle'})
            if role_tag:
                profile_info['role'] = role_tag.text.strip()
            
            # Extract the location
            location_tag = soup.find('div', {'class': 'entity-result__secondary-subtitle'})
            if location_tag:
                profile_info['location'] = location_tag.text.strip()
            
            # Extract the connection degree
            connection_tag = soup.find('span', {'class': 'entity-result__badge-text'})
            if connection_tag:
                profile_info['connection'] = connection_tag.text.strip()
            
            # Extract services
            services_tag = soup.find('strong')
            if services_tag:
                profile_info['services'] = services_tag.text.strip()
            
            # Extract the profile URL
            profile_url_tag = soup.find('a', {'class': 'app-aware-link'}, href=True)
            if profile_url_tag:
                profile_info['profile_url'] = self.clean_profile_url(profile_url_tag['href'])
                
            profiles['data'].append(profile_info)

        return profiles
    
    def save_extracted_data(self, data, page_number):
        path = f"{self.folders[0]}/output_{page_number}.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def send_connection_request(self, profile_url: str, message=str) -> bool:
        self.driver.get(profile_url)
        time.sleep(5)
        
        # Click on "Connect" button
        css_path_connect = "html > body > div:nth-of-type(5) > div:nth-of-type(3) > div > div > div:nth-of-type(2) > div > div > main > section:first-of-type > div:nth-of-type(2) > div:nth-of-type(3) > div > button"
        
        # Do Click on Connect button
        try:
            connect_button_element = self.driver.find_element(By.CSS_SELECTOR, css_path_connect)
            connect_button_element.click()
        except Exception as e:
            print(f"Error: {e}")
            return False

        time.sleep(5)

        # Click on "Add Note" button
        css_path_add_note = "html > body > div:nth-of-type(3) > div > div > div:nth-of-type(3) > button:first-of-type"
        try:
            connect_button_element = self.driver.find_element(By.CSS_SELECTOR, css_path_add_note)
            connect_button_element.click()
        except Exception as e:
            print(f"Error: {e}")
            return False
        time.sleep(5)
        # Add custom message to the connection request
        css_path_text_area = "html > body > div:nth-of-type(3) > div > div > div:nth-of-type(3) > div:first-of-type > textarea"
        try:
            text_area_element = self.driver.find_element(By.CSS_SELECTOR, css_path_text_area)
            text_area_element.send_keys(message)
        except Exception as e:
            print(f"Error: {e}")
            return False
        
        time.sleep(5)
        # Send the connection request   
        css_path_send_message =   "html > body > div:nth-of-type(3) > div > div > div:nth-of-type(4) > button:nth-of-type(2)"
        try:
            send_button_element = self.driver.find_element(By.CSS_SELECTOR, css_path_send_message)
            print(send_button_element.text)
            # send_button_element.click()

        except Exception as e:
            print(f"Error: {e}")
            return False
        time.sleep(5)

        print("Done message request!")
        return True
                
    def run(self, username: str, password: str, search_pattern: str, page_start:int , page_end:int):
        self.login(username=username, password=password)
        self.search_and_extract(search_pattern, page_start, page_end)
        
        # Load some profile 
        # profile_test = "https://www.linkedin.com/in/fernando-terrazas-79abab5/"
        # self.send_connection_request(profile_test)

        time.sleep(20)
        self.driver.quit()

def main():
    scraper = LinkedInScraper()
    
    username = ""# CONFIG['username']
    password = ""#CONFIG['password']
    
    search_pattern = "c# developer"
    page_start = 1
    page_end = 4

    scraper.run(username, password, search_pattern, page_start, page_end)
    
    print("Done! Check the output folder for the extracted data.")

if __name__ == "__main__":
    main()
