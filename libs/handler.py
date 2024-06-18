from typing import List, Union

from libs.linkedin_scraper import LinkedInScraper
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from data_source.kafka import KafkaHandler
from utils.commons import transform_data
from utils.api import (make_post_request, 
                       make_put_request)
from typing import List, Union


def check(list):
    return all(i == list[0] for i in list)

class ScraperHandler:
    def __init__(self,
                 topic_query: str, 
                 topic_data: str, 
                 bootstrap_servers: List[str],
                 api_url: str,
                 debug: bool = True,
                 scraper: LinkedInScraper = None
                 ):
        
        self.kafka_handler = KafkaHandler(
            topic_name=topic_query, 
            bootstrap_servers=bootstrap_servers)

        self.lkdn_handler: LinkedInScraper = scraper
        self.topic = topic_query
        self.topic_data = topic_data
        self.api_url = api_url
        self.debug  = debug

    async def produce(self, producer: AIOKafkaProducer):
        # Produce a message
        data = {
            'search_pattern': 'kafka developer', 
            "page_start": 1,
            "page_end": 4
        }
        
        await producer.send_and_wait(self.topic, value=data)
        await producer.flush()
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
            
    async def send_data(self, output_data_list):
        status_ok = []
        status_fail = []
        for i, data in enumerate(output_data_list):
            
            page  = data['page']
            search_url = data['search_url']
            
            for profile in data['data']:
                clean_data = transform_data(profile, page, search_url)
                # Send to API
                res = await make_post_request(url=self.api_url + "/v1/profile", data=clean_data, headers=None)
                if res is not None:
                    status_ok.append('OK')
                else:
                    status_fail.append({"profile": clean_data, "res":  res})
                    
        return status_ok, status_fail
    
    async def consume_search(self, consumer: AIOKafkaConsumer):

        # Consume messages
        async for message in consumer:
            print("Consumed message from Kafka topic:", message.value)
            
            data: dict = message.value 
            # Topic
            task_id = data['task_id']
            
            output_data_list = await self.lkdn_handler.extract_from_url(**data, debug=self.debug)
            if output_data_list is None:
                print("No data extracted")
                continue
            
            status_ok, status_fail = await self.send_data(output_data_list)  
                
            if check(status_ok):
                await self.update_task(task_id, "OK" )
            else:
                await self.update_task(task_id, "WITH ISSUES")
                print(status_fail)

    async def consume_message(self, consumer: AIOKafkaConsumer):

        # Consume messages
        async for message in consumer:
            print("Consumed message from Kafka:", message.value)
            
            data: dict = message.value
            task_id = data['task_id']
            
            connection_request_status = await self.lkdn_handler.send_connection_request(
                data['profile_url'], data['message'], )
            
            if connection_request_status:
                await self.update_task(task_id, "OK" )
            else:
                await self.update_task(task_id, "FAIL" )


    async def update_task(self, task_id, status):
        payload = {
            "task_status": status
        }
        res = await make_put_request(url=self.api_url + f"/v1/tasks/{task_id}" , data=payload, headers=None)
        
        if res.json()["status_code"] == 201:
            print("OK")
        else:
            print("ERROR IN TASK UPDATE")
        
                            
    async def run(self, ):
        print("running...")
        consumer: AIOKafkaConsumer = self.kafka_handler.get_async_consumer()
        
        if self.topic_data == 'SEARCH':
            await self.consume_search(consumer)

        if self.topic_data == 'MESSAGE':
            await self.consume_message(consumer)