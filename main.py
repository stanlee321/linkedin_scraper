from libs.linkedin_scraper import LinkedInScraper
from kafka import KafkaProducer, KafkaConsumer
from data_source.kafka import KafkaHandler
from utils.commons import transform_data
from utils.api import make_post_request
import logging
import sys
from typing import List, Union


# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# logger = logging.getLogger('kafka')
# logger.setLevel(logging.WARN)



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
        
    def create_payload(self, data: dict) -> Union[dict, None]:
                                
        page_start = data.get('start_at', 1)
        page_end = data.get('end_at', 5)
        geo_urns = data.get('geo_urns', ["104379274"])
        industries = data.get('industries', ["2358","14","4","43"])
        profile_language = data.get('profile_language', ['es'])
        keywords = data.get('search_pattern', '')
                
        kwargs = {
            'page_start': page_start,
            'page_end': page_end,
            'geo_urns': geo_urns,
            'industries': industries,
            'keywords': keywords,
            'profile_language': profile_language
        }
        
        return kwargs
            
    def consume(self, producer: KafkaProducer, consumer: KafkaConsumer, ):

        # Consume messages
        for message in consumer:
            print("Consumed message from Kafka topic:", message.value)
            
            data: dict = message.value 

            # output_data_list = self.lkdn_handler.search_and_extract(**kwargs, debug=self.debug)
            output_data_list = self.lkdn_handler.extract_from_url(**data, debug=self.debug)
            if output_data_list is None:
                print("No data extracted")
                continue
            for i, data in enumerate(output_data_list):
                
                page  = data['page']
                search_url = data['search_url']
                
                for profile in data['data']:
                    clean_data = transform_data(profile, page, search_url)
                    # producer.send(self.topic_data, value=clean_data)     
                    # sproducer.flush()
                    
                    # Send to API
                    res = make_post_request(url=self.api_url, data=clean_data, headers=None)
                    if res is not None:
                        print("Data sent to API OK" )
                    
    def run(self):
        print("runnning...")
        producer: KafkaProducer = self.kafka_handler.get_producer()
        consumer: KafkaConsumer = self.kafka_handler.get_consumer()
        
        # self.produce(producer)
        self.consume(producer, consumer )

        
def main():
    bootstrap_servers = ['192.168.1.9:9093']
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