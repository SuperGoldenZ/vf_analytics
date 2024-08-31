import os
import argparse
from confluent_kafka import Producer
import youtube_helper

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


def produce_from_youtube_playlist(playlist_url):
    urls = youtube_helper.get_video_urls_from_playlist(playlist_url)
    for url in urls:
        print(f"{url}")
        # producer.produce(topic="youtube_urls", value=url)


# Kafka topic to subscribe to
TOPIC = "youtube_urls"

parser = argparse.ArgumentParser(
    description="Send list of videos to process to Kafka for queueing"
)
parser.add_argument(
    "--video_file", help="Local text file containing list of YouTube URLs to process"
)

args = parser.parse_args()

# Create the Kafka consumer
producer = Producer(conf)

with open(vars(args)["video_file"], "r") as fd:
    for line in fd:
        if "watch?v=" in line:
            producer.produce(topic="youtube_urls", value=line.strip())
            producer.flush()
        elif "playlist" in line:
            produce_from_youtube_playlist(line.strip())
