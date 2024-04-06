from libs.linkedin_scraper import LinkedInScraper
from kafka import KafkaProducer, KafkaConsumer
from data_source.kafka import KafkaHandler
from utils.commons import transform_data
from utils.api import make_post_request

from typing import List


class ScraperHandler:
    def __init__(self, 
                 username:str,
                 password:str, 
                 topic_query: str, 
                 topic_data: str, 
                 bootstrap_servers: List[str],
                 api_url: str,
                 debug: bool = True
                 ):
        
        self.kafka_handler = KafkaHandler(
            topic_name=topic_query, 
            bootstrap_servers=bootstrap_servers)

        self.lkdn_handler = LinkedInScraper()
        self.lkdn_handler.login(username=username, password=password)
        self.topic = topic_query
        self.topic_data = topic_data
        self.api_url = api_url
        self.debug  = debug

    def produce(self, producer: KafkaProducer):

        # Produce a message
        data = {
            'search_pattern': 'kafka developer', 
            "page_start": 1,
            "page_end": 4
        }
        
        producer.send(self.topic, value=data)
        producer.flush()
        print("Message produced to Kafka topic:", self.topic)

    def consume(self, producer: KafkaProducer , consumer: KafkaConsumer, ):

        # Consume messages
        for message in consumer:
            print("Consumed message from Kafka topic:", message.value)
            
            data = message.value
            search_pattern = data['search_pattern']
            page_start = data['start_at']
            page_end = data['end_at']
            
            # Instrction : SCRAP
            output_data_list = self.lkdn_handler.search_and_extract(search_pattern, page_start, page_end, debug=self.debug)
            
            for i, data in enumerate(output_data_list):
                page  = data['page']
                for profile in data['data']:
                    if not(profile['name'] == '' or profile['profile_url']  == ''):
                        clean_data = transform_data(profile, page)
                        producer.send(self.topic_data, value=clean_data)     
                        producer.flush()
                        
                        # Send to API
                        make_post_request(url=self.api_url, data=clean_data, headers=None)
                        
                        

    def run(self):
        print("runnning...")
        producer: KafkaProducer = self.kafka_handler.get_producer()
        consumer: KafkaConsumer = self.kafka_handler.get_consumer()
        
        # self.produce(producer)
        self.consume(producer, consumer )

        
def main():
    bootstrap_servers = ['192.168.1.16:9093']
    topic_query = "query"
    topic_profiles = "profiles"
    
    api_url = 'http://127.0.0.1:8000/v1/profile'
    debug = False
    
    scraper_handler = ScraperHandler(
        username = username,
        password = password,
        topic_query=topic_query,
        topic_data=topic_profiles,
        bootstrap_servers = bootstrap_servers,
        api_url=api_url,
        debug = debug
    )
    
    scraper_handler.run()


if __name__ == '__main__':
    main()