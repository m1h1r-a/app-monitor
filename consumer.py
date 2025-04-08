import json
import os
import threading
import time
from datetime import datetime

import pymysql
from confluent_kafka import Consumer
from prometheus_client import Counter, Summary, start_http_server

# use env variables from docker-compose.yml
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9092")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysql")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "log_monitoring")

print(f"DEBUG - KAFKA_BROKER value: '{KAFKA_BROKER}'")

TOPICS = ["api_errors", "api_requests", "api_responses"]
GROUP_ID = "log-consumer-group"

# retry mysql connection
max_retries = 10
retry_delay = 5
connected = False
db = None

print(f"Attempting to connect to MySQL at {MYSQL_HOST}:{MYSQL_PORT}...")

for attempt in range(max_retries):
    try:
        db = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
        connected = True
        print(f"Successfully connected to MySQL database '{MYSQL_DATABASE}'")
        break
    except Exception as e:
        print(f"Connection attempt {attempt+1}/{max_retries} failed: {str(e)}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

if not connected:
    print("Failed to connect to MySQL after multiple attempts. Exiting.")
    exit(1)

# Use explicit config dictionary for clearer debugging
kafka_config = {
    "bootstrap.servers": KAFKA_BROKER,
    "group.id": GROUP_ID,
    "auto.offset.reset": "earliest",
}

print(f"Initializing Kafka consumer with config: {kafka_config}")
consumer = Consumer(kafka_config)

print(f"Subscribing to Kafka topics: {TOPICS}")
consumer.subscribe(TOPICS)

consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
    }
)
consumer.subscribe(TOPICS)

# Prometheus metrics
REQUEST_COUNTER = Counter(
    "api_requests_total", "Total number of API requests", ["endpoint", "method"]
)
RESPONSE_COUNTER = Counter(
    "api_responses_total", "Total number of API responses", ["endpoint", "status_code"]
)
ERROR_COUNTER = Counter(
    "api_errors_total", "Total number of API errors", ["endpoint", "error"]
)
RESPONSE_TIME = Summary(
    "api_response_time_seconds", "API response time in seconds", ["endpoint"]
)


# Start Prometheus server on port 8000
def start_prometheus_server():
    start_http_server(8000)
    print("Prometheus metrics available at http://localhost:8000/metrics")


threading.Thread(target=start_prometheus_server, daemon=True).start()


def insert_log(log):
    try:
        with db.cursor() as cursor:
            query = """
            INSERT INTO logs (
                endpoint, method, status_code, response, response_time,
                error, log_level, metadata, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    log["endpoint"],
                    log["method"],
                    log["status_code"],
                    log["response"],
                    log["response_time"],
                    log["error"],
                    log["log_level"],
                    None,
                    log["timestamp"],
                ),
            )
    except Exception as e:
        print(f"MySQL insert error: {e}")


def build_log(
    endpoint, method, status_code, response, response_time, error, log_level, timestamp
):
    return {
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "response": response,
        "response_time": response_time,
        "error": error,
        "log_level": log_level,
        "timestamp": timestamp,
    }


print(f"Listening to Kafka topics: {TOPICS}...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Kafka error: {msg.error()}")
            continue

        topic = msg.topic()
        data = json.loads(msg.value().decode("utf-8"))

        print(f"\nReceived message from {topic}:")
        print(json.dumps(data, indent=2))

        timestamp = datetime.now()

        if data.get("event") == "API Request":
            endpoint = data.get("endpoint")
            method = data.get("method")

            REQUEST_COUNTER.labels(endpoint=endpoint, method=method).inc()

            log = build_log(endpoint, method, 0, 0, 0.0, None, "Request", timestamp)
            insert_log(log)

        elif data.get("event") == "API Response":
            endpoint = data.get("endpoint")
            status_code = data.get("status_code")
            response = data.get("response", {})
            response_time = response.get("response_time", 0.0)

            RESPONSE_COUNTER.labels(endpoint=endpoint, status_code=status_code).inc()
            RESPONSE_TIME.labels(endpoint=endpoint).observe(response_time)

            log = build_log(
                endpoint,
                "N/A",
                status_code,
                1,
                response_time,
                None,
                "Response",
                timestamp,
            )
            insert_log(log)

        elif data.get("event") == "API Error":
            endpoint = data.get("endpoint")
            error = data.get("error")
            status_code = data.get("status_code", 500)

            ERROR_COUNTER.labels(endpoint=endpoint, error=error).inc()

            log = build_log(
                endpoint, "N/A", status_code, 0, 0.0, error, "Error", timestamp
            )
            insert_log(log)

except KeyboardInterrupt:
    print("\nStopping consumer...")
finally:
    consumer.close()
