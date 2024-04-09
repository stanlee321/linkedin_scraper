from kafka import KafkaProducer, KafkaConsumer
import json
from typing import List

class KafkaHandler:
    def __init__(self, topic_name: str, bootstrap_servers: List[str]):
        # Kafka Consumer
        self.consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='my-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        # Kafka Producer
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
    def get_consumer(self):
        return self.consumer

    def get_producer(self):
        return self.producer
