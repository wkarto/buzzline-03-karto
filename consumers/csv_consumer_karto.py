"""
csv_consumer_karto.py

Consume JSON-transferred CSV messages from a Kafka topic and process them.

Customized for delivery_status data: timestamp, package_id, status
"""

#####################################
# Import Modules
#####################################
import os
import json
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

#####################################
# Process single message
#####################################
def process_message(message: str) -> None:
    """
    Processes a delivery_status message
    """
    try:
        data: dict = json.loads(message)
        timestamp = data.get("timestamp")
        package_id = data.get("package_id")
        status = data.get("status")

        if not all([timestamp, package_id, status]):
            logger.error(f"[Karto CSV Consumer] Invalid message format: {message}")
            return

        logger.info(f"[Karto CSV Consumer] Package '{package_id}' at '{timestamp}' has status: {status}")

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
    consumer = create_kafka_consumer(topic, group_id)

    logger.info(f"[Karto CSV Consumer] Polling messages from topic '{topic}'...")
    try:
        for message in consumer:
            message_str = message.value
            logger.debug(f"[Karto CSV Consumer] Received message at offset {message.offset}: {message_str}")
            process_message(message_str)
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
