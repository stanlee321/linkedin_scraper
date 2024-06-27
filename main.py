import yaml
import logging
import sys
import asyncio
from libs.linkedin_scraper import LinkedInScraper
from libs.handler import ScraperHandler
from config.util import Environment
import json



class Config:
    def __init__(self):
        self.bootstrap_servers = json.loads(Environment.get_string("BOOTSTRAP_SERVERS", '["192.168.1.12:9093"]'))
        self.topics = json.loads(Environment.get_string("TOPICS", '["SEARCH", "MESSAGE"]'))
        self.username = Environment.get_string("USERNAME", "a@gmail.com")
        self.password = Environment.get_string("PASSWORD", "!!!")
        self.api_url = Environment.get_string("API_URL", "http://localhost:5000")
        self.debug = Environment.get_string("DEBUG", "0")
        self.headless = Environment.get_string("HEADLESS", "0")
    
    def to_json(self):
        return {
            "bootstrap_servers": self.bootstrap_servers,
            "topics": self.topics,
            "username": self.username,
            "password": self.password,
            "api_url": self.api_url,
            "debug": self.debug,
            "headless": self.headless
        }



def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

async def main():
    print("Starting Scraper")
    # Load configuration
    config = Config()
    
    # Parse topics string to list
    topics = config.topics
    bootstrap_servers = config.bootstrap_servers

    print(f"Topics: {topics}")
    print(f"Bootstrap servers: {bootstrap_servers}")
    
    print(f"Config: {config.to_json()}")
    headless = True if config.headless == "1" else False
    linkedin_scraper = LinkedInScraper(headless=headless)
    linkedin_scraper.login(username=config.username, 
                           password=config.password)

    

    # Create two instances of ScraperHandler
    scraper_handler1 = ScraperHandler(
        topic_query=topics[0],
        topic_data=topics[0],
        bootstrap_servers = bootstrap_servers,
        api_url=config.api_url,
        debug=config.debug,
        scraper = linkedin_scraper
    )

    scraper_handler2 = ScraperHandler(
        topic_query=topics[1],
        topic_data=topics[1],
        bootstrap_servers = bootstrap_servers,
        api_url= config.api_url,
        debug = config.debug,
        scraper = linkedin_scraper
    )
    
    # Run both handlers concurrently
    await asyncio.gather(
        scraper_handler1.run(),
        scraper_handler2.run()
    )

if __name__ == '__main__':
    asyncio.run(main())