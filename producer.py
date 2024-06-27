from kafka import KafkaProducer
import json


producer = KafkaProducer(
    bootstrap_servers='192.168.1.12:9093',  # Adjust this to your Kafka broker address
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Produce a message to SEARCH topic
search_message = {
    'search_pattern': 'kafka developer',
    'page_start': 1,
    'page_end': 4,
    'task_id': 'search_task_1'
}
producer.send('SEARCH', value=search_message)
print("Message produced to SEARCH topic:", search_message)

# Produce a message to MESSAGE topic
message_data = {
    'profile_url': 'https://www.linkedin.com/in/sample-profile/',
    'message': 'Hello, this is a test connection request.',
    'task_id': 'message_task_1'
}
producer.send('MESSAGE', value=message_data)
print("Message produced to MESSAGE topic:", message_data)

# Flush the producer to ensure all messages are sent
producer.flush()