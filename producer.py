import json

from confluent_kafka import Producer

KAFKA_BROKER = "localhost:9092"
TOPIC_REQUESTS = "api_requests"
TOPIC_RESPONSES = "api_responses"
TOPIC_ERRORS = "api_errors"


producer = Producer({"bootstrap.servers": KAFKA_BROKER})


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


def log_error(endpoint, error_message):
    """Log API errors to Kafka."""
    log_data = {"event": "API Error", "endpoint": endpoint, "error": error_message}
    message = json.dumps(log_data).encode("utf-8")
    producer.produce(TOPIC_ERRORS, value=message)
    producer.flush()
    print(f"Sent to Kafka ({TOPIC_ERRORS}): {log_data}")
