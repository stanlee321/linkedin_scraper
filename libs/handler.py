from typing import List, Union
import uuid
import json
from libs.linkedin_scraper import LinkedInScraper
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from utils.commons import transform_data
from utils.api import (make_post_request, 
                       make_put_request)


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

        self.bootstrap_servers = bootstrap_servers
        self.lkdn_handler: LinkedInScraper = scraper
        self.topic_query = topic_query
        self.topic_data = topic_data
        self.api_url = api_url
        self.debug  = debug
        self.group_id = str(uuid.uuid4())  # Generate a unique UUID for group_id


    async def async_producer(self, producer: AIOKafkaProducer):
        # Produce a message
        data = {
            'search_pattern': 'kafka developer', 
            "page_start": 1,
            "page_end": 4
        }
        
        await producer.send_and_wait(self.topic, value=data)
        await producer.flush()
        print("Message produced to Kafka topic:", self.topic)
        
    async def get_async_consumer(self):
        consumer = AIOKafkaConsumer(
            self.topic_query,
            self.topic_data,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset='earliest'
        )
        return consumer

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
        
        print("Consuming messages from Kafka topic:", self.topic_data)
        # Consume messages
        try:   
            async for message in consumer:
                print("Consumed message from Kafka topic:", message.value)
                
                data: dict = json.loads(message.value.decode('utf-8'))  # Decode and deserialize the message
                
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
        finally:
            await consumer.stop()

    async def consume_message(self, consumer: AIOKafkaConsumer):
        print("Consuming messages from Kafka topic:", self.topic_data)
        # Consume messages
        async for message in consumer:
            print("Consumed message from Kafka:", message.value)
            
            data: dict = json.loads(message.value.decode('utf-8'))  # Decode and deserialize the message
            task_id = data['task_id']
            
            connection_request_status = self.lkdn_handler.send_connection_request(
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
        
        if res is not None and res.json()["status_code"] == 201:
            print("OK")
        else:
            print("ERROR IN TASK UPDATE")
        

    async def run(self, ):
        print("running...")
        consumer: AIOKafkaConsumer = await self.get_async_consumer()
        await consumer.start()
    
        if self.topic_data == 'SEARCH':
            await self.consume_search(consumer)

        if self.topic_data == 'MESSAGE':
            await self.consume_message(consumer)