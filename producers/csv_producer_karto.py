"""
csv_producer_karto.py

Stream numeric CSV data to a Kafka topic.

This is a direct customization of the base CSV producer.
"""

#####################################
# Import Modules
#####################################

import os
import sys
import time
import pathlib
import csv
import json
from datetime import datetime

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
# Getter Functions
#####################################

def get_kafka_topic() -> str:
    topic = os.getenv("SMOKER_TOPIC", "unknown_topic")
    logger.info(f"[Karto CSV Producer] Kafka topic: {topic}")
    return topic

def get_message_interval() -> int:
    interval = int(os.getenv("SMOKER_INTERVAL_SECONDS", 1))
    logger.info(f"[Karto CSV Producer] Message interval: {interval} seconds")
    return interval

#####################################
# Set up Paths
#####################################

PROJECT_ROOT = pathlib.Path(__file__).parent.parent
logger.info(f"[Karto CSV Producer] Project root: {PROJECT_ROOT}")

DATA_FOLDER = PROJECT_ROOT.joinpath("data")
logger.info(f"[Karto CSV Producer] Data folder: {DATA_FOLDER}")

DATA_FILE = DATA_FOLDER.joinpath("smoker_temps.csv")
logger.info(f"[Karto CSV Producer] Data file: {DATA_FILE}")

#####################################
# Message Generator
#####################################

def generate_messages(file_path: pathlib.Path):
    while True:
        try:
            logger.info(f"[Karto CSV Producer] Opening data file: {DATA_FILE}")
            with open(DATA_FILE, "r") as csv_file:
                logger.info(f"[Karto CSV Producer] Reading data from file: {DATA_FILE}")
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    if "temperature" not in row:
                        logger.error(f"Missing 'temperature' column in row: {row}")
                        continue
                    current_timestamp = datetime.utcnow().isoformat()
                    message = {
                        "timestamp": current_timestamp,
                        "temperature": float(row["temperature"]),
                    }
                    logger.debug(f"[Karto CSV Producer] Generated message: {message}")
                    yield message
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}. Exiting.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error in message generation: {e}")
            sys.exit(3)

#####################################
# Main Function
#####################################

def main():
    logger.info("[Karto CSV Producer] START producer.")
    verify_services()

    topic = get_kafka_topic()
    interval_secs = get_message_interval()

    if not DATA_FILE.exists():
        logger.error(f"Data file not found: {DATA_FILE}. Exiting.")
        sys.exit(1)

    producer = create_kafka_producer(
        value_serializer=lambda x: json.dumps(x).encode("utf-8")
    )
    if not producer:
        logger.error("Failed to create Kafka producer. Exiting...")
        sys.exit(3)

    try:
        create_kafka_topic(topic)
        logger.info(f"[Karto CSV Producer] Kafka topic '{topic}' is ready.")
    except Exception as e:
        logger.error(f"Failed to create or verify topic '{topic}': {e}")
        sys.exit(1)

    logger.info(f"[Karto CSV Producer] Starting message production to topic '{topic}'...")
    try:
        for csv_message in generate_messages(DATA_FILE):
            producer.send(topic, value=csv_message)
            logger.info(f"[Karto CSV Producer] Sent message to topic '{topic}': {csv_message}")
            time.sleep(interval_secs)
    except KeyboardInterrupt:
        logger.warning("[Karto CSV Producer] Producer interrupted by user.")
    except Exception as e:
        logger.error(f"[Karto CSV Producer] Error during message production: {e}")
    finally:
        producer.close()
        logger.info("[Karto CSV Producer] Kafka producer closed.")

    logger.info("[Karto CSV Producer] END producer.")

#####################################
# Conditional Execution
#####################################

if __name__ == "__main__":
    main()
