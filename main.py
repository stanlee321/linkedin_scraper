import yaml
import logging
import sys
import asyncio
from libs.linkedin_scraper import LinkedInScraper
from libs.handler import ScraperHandler


def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

async def main():
    config = load_config('config.yaml')

    bootstrap_servers = config['bootstrap_servers']
    topics = config['topics']

    username = config['credentials']['username']
    password = config['credentials']['password']
    api_url = config['api']['url']
    debug = config['debug']
            
    linkedin_scraper = LinkedInScraper()
    linkedin_scraper.login(username=username, password=password)

    # Create two instances of ScraperHandler
    scraper_handler1 = ScraperHandler(
        topic_query=topics[0],
        topic_data=topics[0],
        bootstrap_servers = bootstrap_servers,
        api_url=api_url,
        debug = debug,
        scraper = linkedin_scraper
    )

    scraper_handler2 = ScraperHandler(
        topic_query=topics[1],
        topic_data=topics[1],
        bootstrap_servers = bootstrap_servers,
        api_url=api_url,
        debug = debug,
        scraper = linkedin_scraper
    )
    
    # Run both handlers concurrently
    await asyncio.gather(
        scraper_handler1.run(),
        scraper_handler2.run()
    )

if __name__ == '__main__':
    asyncio.run(main())