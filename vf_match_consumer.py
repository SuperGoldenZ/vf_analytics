import os
import confluent_kafka
from confluent_kafka import Consumer
import vf_match_analyzer

# Kafka configuration
conf = {
    "bootstrap.servers": os.environ["KAFKA_BOOTSTRAP_SERVER"],
    "group.id": "youtube_processor_group",
    "auto.offset.reset": "earliest",
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
        print(f"Received URL: {url}")

        # Process the YouTube video
        vf_match_analyzer.analyze_video(url)

except KeyboardInterrupt:
    pass
finally:
    # Close the consumer
    consumer.close()
