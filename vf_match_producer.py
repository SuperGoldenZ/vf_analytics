import os
import confluent_kafka
from confluent_kafka import Producer
import vf_match_analyzer

# Kafka configuration
conf = {
    "bootstrap.servers": os.environ["KAFKA_BOOTSTRAP_SERVER"],
    "group.id": "youtube_processor_group",
    "auto.offset.reset": "earliest",
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': os.environ["KAFKA_SASL_USERNAME"],
    'sasl.password': os.environ["KAFKA_SASL_PASSWORD"]
}

# Kafka topic to subscribe to
TOPIC = "youtube_urls"

# Create the Kafka consumer
producer = Producer(conf)
producer.produce(topic='youtube_urls', value='https://www.youtube.com/watch?v=qdZceuGlaB4')
producer.flush()

