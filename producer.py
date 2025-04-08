import json
import os
import time

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9092")
print(f"DEBUG - KAFKA_BROKER value: '{KAFKA_BROKER}'")

TOPIC_REQUESTS = "api_requests"
TOPIC_RESPONSES = "api_responses"
TOPIC_ERRORS = "api_errors"


def create_topics():
    print(
        f"Ensuring Kafka topics exist: {TOPIC_REQUESTS}, {TOPIC_RESPONSES}, {TOPIC_ERRORS}"
    )

    admin_client = AdminClient({"bootstrap.servers": KAFKA_BROKER})

    topic_list = [
        NewTopic(TOPIC_REQUESTS, num_partitions=1, replication_factor=1),
        NewTopic(TOPIC_RESPONSES, num_partitions=1, replication_factor=1),
        NewTopic(TOPIC_ERRORS, num_partitions=1, replication_factor=1),
    ]

    # create topics
    try:
        futures = admin_client.create_topics(topic_list)

        for topic, future in futures.items():
            try:
                future.result()
                print(f"Topic {topic} created")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"Topic {topic} already exists")
                else:
                    print(f"Failed to create topic {topic}: {e}")
    except Exception as e:
        print(f"Failed to create topics: {e}")


kafka_config = {"bootstrap.servers": KAFKA_BROKER}

print(f"Initializing Kafka producer with config: {kafka_config}")
producer = Producer(kafka_config)


def log_request(endpoint, method, data=None):
    """Log API requests to Kafka."""
    log_data = {
        "event": "API Request",
        "endpoint": endpoint,
        "method": method,
        "data": data,
    }
    message = json.dumps(log_data).encode("utf-8")
    producer.produce(TOPIC_REQUESTS, value=message)
    producer.flush()
    print(f"Sent to Kafka ({TOPIC_REQUESTS}): {log_data}")


def log_response(endpoint, status_code, response_data):
    """Log API responses to Kafka."""
    log_data = {
        "event": "API Response",
        "endpoint": endpoint,
        "status_code": status_code,
        "response": response_data,
    }
    message = json.dumps(log_data).encode("utf-8")
    producer.produce(TOPIC_RESPONSES, value=message)
    producer.flush()
    print(f"Sent to Kafka ({TOPIC_RESPONSES}): {log_data}")


def log_error(endpoint, status_code, error_message):
    """Log API errors to Kafka."""
    log_data = {
        "event": "API Error",
        "endpoint": endpoint,
        "status_code": status_code,
        "error": error_message,
    }
    message = json.dumps(log_data).encode("utf-8")
    producer.produce(TOPIC_ERRORS, value=message)
    producer.flush()
    print(f"Sent to Kafka ({TOPIC_ERRORS}): {log_data}")


# for containerization
if __name__ == "__main__":
    print(f"Producer service started. Connected to Kafka broker: {KAFKA_BROKER}")

    max_retries = 10
    for i in range(max_retries):
        try:
            producer.list_topics(timeout=5)
            print("Successfully connected to Kafka")
            break
        except Exception as e:
            print(f"Kafka not ready yet (attempt {i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("Failed to connect to Kafka after multiple attempts")
                exit(1)

    # create topics
    create_topics()

    # keep container running
    while True:
        time.sleep(60)
