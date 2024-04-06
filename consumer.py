from kafka import KafkaProducer, KafkaConsumer
import json

consumer_client = KafkaConsumer(
    "profiles_2",
    bootstrap_servers=['192.168.1.16:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='profiles-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)
# Consume messages
for message in consumer_client:
    print("Consumed message from Kafka topi.....c:", message.value)
            