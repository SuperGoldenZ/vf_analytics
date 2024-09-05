import os
import logging
import gc
import confluent_kafka
from confluent_kafka import Consumer
import vf_match_analyzer
import traceback

logger = None
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="vf_match_consumer.log", encoding="utf-8", level=logging.INFO
)

# Kafka configuration
conf = {
    "bootstrap.servers": os.environ["KAFKA_BOOTSTRAP_SERVER"],
    "group.id": "youtube_processor_group",
    "auto.offset.reset": "earliest",
    "security.protocol": "SASL_SSL",
    "sasl.mechanism": "PLAIN",
    "sasl.username": os.environ["KAFKA_SASL_USERNAME"],
    "sasl.password": os.environ["KAFKA_SASL_PASSWORD"],
}

# Kafka topic to subscribe to
TOPIC = "youtube_urls"

# Create the Kafka consumer
consumer = Consumer(conf)

# Subscribe to the Kafka topic
consumer.subscribe([TOPIC])

# Main processing loop
try:
    while True:
        msg = consumer.poll(1.0)  # Poll for new messages

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == confluent_kafka.KafkaError._PARTITION_EOF:
                # End of partition event
                continue
            else:
                # Error
                print(msg.error())
                break

        # Get the YouTube URL from the message
        url = msg.value().decode("utf-8")
        print(f"Received URL: {url}", end=" ", flush=True)

        try:
            vf_match_analyzer.analyze_video(url)
            gc.collect()
        except Exception as e:
            print(f"\terror occured processing {url}, skipping video")
            print(e)
            print(traceback.format_exc())

        # Process the YouTube video
        print("done!", flush=True)

except KeyboardInterrupt:
    pass
finally:
    print("Closing consumer")
    # Close the consumer
    consumer.close()
