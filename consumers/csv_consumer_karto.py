"""
csv_consumer_karto.py

Consume JSON-transferred CSV messages from a Kafka topic and process them.

This is a direct customization of the base CSV consumer.
"""

#####################################
# Import Modules
#####################################

import os
import json
from collections import deque

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
    topic = os.getenv("SMOKER_TOPIC", "unknown_topic")
    logger.info(f"[Karto CSV Consumer] Kafka topic: {topic}")
    return topic

def get_kafka_consumer_group_id() -> str:
    group_id: str = os.getenv("SMOKER_CONSUMER_GROUP_ID", "default_group")
    logger.info(f"[Karto CSV Consumer] Kafka consumer group id: {group_id}")
    return group_id

def get_stall_threshold() -> float:
    temp_variation = float(os.getenv("SMOKER_STALL_THRESHOLD_F", 0.2))
    logger.info(f"[Karto CSV Consumer] Max stall temperature range: {temp_variation} F")
    return temp_variation

def get_rolling_window_size() -> int:
    window_size = int(os.getenv("SMOKER_ROLLING_WINDOW_SIZE", 5))
    logger.info(f"[Karto CSV Consumer] Rolling window size: {window_size}")
    return window_size

#####################################
# Detect stall
#####################################

def detect_stall(rolling_window_deque: deque) -> bool:
    WINDOW_SIZE: int = get_rolling_window_size()
    if len(rolling_window_deque) < WINDOW_SIZE:
        logger.debug(f"[Karto CSV Consumer] Rolling window size: {len(rolling_window_deque)}. Waiting for {WINDOW_SIZE}.")
        return False

    temp_range = max(rolling_window_deque) - min(rolling_window_deque)
    is_stalled: bool = temp_range <= get_stall_threshold()
    logger.debug(f"[Karto CSV Consumer] Temperature range: {temp_range}°F. Stalled: {is_stalled}")
    return is_stalled

#####################################
# Process single message
#####################################

def process_message(message: str, rolling_window: deque, window_size: int) -> None:
    try:
        logger.debug(f"[Karto CSV Consumer] Raw message: {message}")
        data: dict = json.loads(message)
        temperature = data.get("temperature")
        timestamp = data.get("timestamp")
        logger.info(f"[Karto CSV Consumer] Processed JSON message: {data}")

        if temperature is None or timestamp is None:
            logger.error(f"[Karto CSV Consumer] Invalid message format: {message}")
            return

        rolling_window.append(temperature)

        if detect_stall(rolling_window):
            logger.info(f"[Karto CSV Consumer] STALL DETECTED at {timestamp}: Temp stable at {temperature}°F over last {window_size} readings.")

    except json.JSONDecodeError as e:
        logger.error(f"[Karto CSV Consumer] JSON decoding error for message '{message}': {e}")
    except Exception as e:
        logger.error(f"[Karto CSV Consumer] Error processing message '{message}': {e}")

#####################################
# Main Function
#####################################

def main() -> None:
    logger.info("[Karto CSV Consumer] START consumer.")

    topic = get_kafka_topic()
    group_id = get_kafka_consumer_group_id()
    window_size = get_rolling_window_size()
    logger.info(f"[Karto CSV Consumer] Consumer: Topic '{topic}' and group '{group_id}'...")
    logger.info(f"[Karto CSV Consumer] Rolling window size: {window_size}")

    rolling_window = deque(maxlen=window_size)
    consumer = create_kafka_consumer(topic, group_id)

    logger.info(f"[Karto CSV Consumer] Polling messages from topic '{topic}'...")
    try:
        for message in consumer:
            message_str = message.value
            logger.debug(f"[Karto CSV Consumer] Received message at offset {message.offset}: {message_str}")
            process_message(message_str, rolling_window, window_size)
    except KeyboardInterrupt:
        logger.warning("[Karto CSV Consumer] Consumer interrupted by user.")
    except Exception as e:
        logger.error(f"[Karto CSV Consumer] Error while consuming messages: {e}")
    finally:
        consumer.close()
        logger.info(f"[Karto CSV Consumer] Kafka consumer for topic '{topic}' closed.")

#####################################
# Conditional Execution
#####################################

if __name__ == "__main__":
    main()
