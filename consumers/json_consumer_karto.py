"""
json_consumer_karto.py

Consume JSON messages from a Kafka topic and process them.

This is a direct customization of the base JSON consumer.
"""

#####################################
# Import Modules
#####################################

import os
import json
from collections import defaultdict

from dotenv import load_dotenv
from utils.utils_consumer import create_kafka_consumer
from utils.utils_logger import logger

#####################################
# Load Environment Variables
#####################################

load_dotenv()

#####################################
# Getter Functions
#####################################

def get_kafka_topic() -> str:
    topic = os.getenv("BUZZ_TOPIC", "unknown_topic")
    logger.info(f"[Karto JSON Consumer] Kafka topic: {topic}")
    return topic

def get_kafka_consumer_group_id() -> str:
    group_id: str = os.getenv("BUZZ_CONSUMER_GROUP_ID", "default_group")
    logger.info(f"[Karto JSON Consumer] Kafka consumer group id: {group_id}")
    return group_id

#####################################
# Data Store for Author Counts
#####################################

author_counts: defaultdict[str, int] = defaultdict(int)

#####################################
# Function to Process a Single Message
#####################################

def process_message(message: str) -> None:
    try:
        logger.debug(f"[Karto JSON Consumer] Raw message: {message}")
        from typing import Any
        message_dict: dict[str, Any] = json.loads(message)
        logger.info(f"[Karto JSON Consumer] Processed JSON message: {message_dict}")

        author = message_dict.get("author", "unknown")
        logger.info(f"[Karto JSON Consumer] Message received from author: {author}")

        author_counts[author] += 1
        logger.info(f"[Karto JSON Consumer] Updated author counts: {dict(author_counts)}")

    except json.JSONDecodeError:
        logger.error(f"[Karto JSON Consumer] Invalid JSON message: {message}")
    except Exception as e:
        logger.error(f"[Karto JSON Consumer] Error processing message: {e}")

#####################################
# Main Function
#####################################

def main() -> None:
    logger.info("[Karto JSON Consumer] START consumer.")

    topic = get_kafka_topic()
    group_id = get_kafka_consumer_group_id()
    logger.info(f"[Karto JSON Consumer] Consumer: Topic '{topic}' and group '{group_id}'...")

    consumer = create_kafka_consumer(topic, group_id)

    logger.info(f"[Karto JSON Consumer] Polling messages from topic '{topic}'...")
    try:
        while True:
            records = consumer.poll(timeout_ms=1000, max_records=100)
            if not records:
                continue
            for _tp, batch in records.items():
                for msg in batch:
                    message_str: str = msg.value
                    logger.debug(f"[Karto JSON Consumer] Received message at offset {msg.offset}: {message_str}")
                    process_message(message_str)
    except KeyboardInterrupt:
        logger.warning("[Karto JSON Consumer] Consumer interrupted by user.")
    except Exception as e:
        logger.error(f"[Karto JSON Consumer] Error while consuming messages: {e}")
    finally:
        consumer.close()
        logger.info(f"[Karto JSON Consumer] Kafka consumer for topic '{topic}' closed.")

    logger.info(f"[Karto JSON Consumer] END consumer for topic '{topic}' and group '{group_id}'.")

#####################################
# Conditional Execution
#####################################

if __name__ == "__main__":
    main()
