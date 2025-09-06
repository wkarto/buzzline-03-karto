"""
json_producer_karto.py

Custom JSON Kafka producer by Karto.
Based on the original json_producer_case.py script.

Streams JSON data from buzz.json to a Kafka topic.
"""

#####################################
# Import Modules
#####################################

import os
import sys
import time
import pathlib
import json
from typing import Generator, Dict, Any

from dotenv import load_dotenv

from utils.utils_producer import (
    verify_services,
    create_kafka_producer,
    create_kafka_topic,
)
from utils.utils_logger import logger

#####################################
# Load Environment Variables
#####################################

load_dotenv()

#####################################
# Getter Functions for .env Variables
#####################################


def get_kafka_topic() -> str:
    topic = os.getenv("BUZZ_TOPIC", "unknown_topic")
    logger.info(f"[Karto Producer] Kafka topic: {topic}")
    return topic


def get_message_interval() -> int:
    interval = int(os.getenv("BUZZ_INTERVAL_SECONDS", 1))
    logger.info(f"[Karto Producer] Message interval: {interval} seconds")
    return interval


#####################################
# Set up Paths
#####################################

PROJECT_ROOT = pathlib.Path(__file__).parent.parent
logger.info(f"[Karto Producer] Project root: {PROJECT_ROOT}")

DATA_FOLDER: pathlib.Path = PROJECT_ROOT.joinpath("data")
logger.info(f"[Karto Producer] Data folder: {DATA_FOLDER}")

DATA_FILE: pathlib.Path = DATA_FOLDER.joinpath("custom_stock_alerts.json")
logger.info(f"Data file: {DATA_FILE}")

#####################################
# Message Generator
#####################################


def generate_messages(file_path: pathlib.Path) -> Generator[Dict[str, Any], None, None]:
    while True:
        try:
            logger.info(f"[Karto Producer] Opening file: {file_path}")
            with open(file_path, "r") as json_file:
                json_data: list[Dict[str, Any]] = json.load(json_file)

                for entry in json_data:
                    logger.debug(f"[Karto Producer] Generated JSON: {entry}")
                    yield entry

        except FileNotFoundError:
            logger.error(f"[Karto Producer] File not found: {file_path}. Exiting.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"[Karto Producer] Invalid JSON format. Error: {e}")
            sys.exit(2)
        except Exception as e:
            logger.error(f"[Karto Producer] Unexpected error: {e}")
            sys.exit(3)


#####################################
# Main Function
#####################################


def main():
    logger.info("[Karto Producer] START producer.")
    verify_services()

    topic = get_kafka_topic()
    interval_secs = get_message_interval()

    if not DATA_FILE.exists():
        logger.error(f"[Karto Producer] Data file not found: {DATA_FILE}. Exiting.")
        sys.exit(1)

    producer = create_kafka_producer(
        value_serializer=lambda x: json.dumps(x).encode("utf-8")
    )
    if not producer:
        logger.error("[Karto Producer] Failed to create Kafka producer. Exiting...")
        sys.exit(3)

    try:
        create_kafka_topic(topic)
        logger.info(f"[Karto Producer] Kafka topic '{topic}' is ready.")
    except Exception as e:
        logger.error(f"[Karto Producer] Failed to create or verify topic '{topic}': {e}")
        sys.exit(1)

    logger.info(f"[Karto Producer] Starting to send messages to '{topic}'...")
    try:
        for message_dict in generate_messages(DATA_FILE):
            producer.send(topic, value=message_dict)
            logger.info(f"[Karto Producer] Sent message: {message_dict}")
            time.sleep(interval_secs)
    except KeyboardInterrupt:
        logger.warning("[Karto Producer] Interrupted by user.")
    except Exception as e:
        logger.error(f"[Karto Producer] Error during production: {e}")
    finally:
        producer.close(timeout=None)
        logger.info("[Karto Producer] Kafka producer closed.")

    logger.info("[Karto Producer] END producer.")


if __name__ == "__main__":
    main()
