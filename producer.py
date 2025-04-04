import json
import time

import requests
from confluent_kafka import Producer

KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "orders"

producer_config = {"bootstrap.servers": KAFKA_BROKER}
producer = Producer(producer_config)

# take orders which are not processed url json-server
JSON_SERVER_ORDERS_URL = "http://localhost:3000/orders?processed=False"
# JSON_SERVER_ORDERS_URL = "http://json-server-container:3000/orders?processed=false"


def fetch_new_orders():
    """Fetch orders from JSON Server where processed is false."""
    try:
        response = requests.get(JSON_SERVER_ORDERS_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching orders: {e}")
        return []


def process_order(order):
    """Produce message for the order and mark it as processed."""
    try:
        order_json = json.dumps(order)
        # Produce message to Kafka topic "orders"
        producer.produce(KAFKA_TOPIC, order_json.encode("utf-8"))
        producer.flush()
        print(f"Produced to Kafka: {order_json}")

        # Mark the order as processed using a PATCH request
        order_id = order["id"]
        patch_url = f"http://localhost:3000/orders/{order_id}"
        patch_data = {"processed": True}
        patch_response = requests.patch(patch_url, json=patch_data)
        if patch_response.status_code in [200, 204]:
            print(f"Order {order_id} marked as processed.")
        else:
            print(
                f"Failed to update order {order_id}: {patch_response.status_code}, {patch_response.text}"
            )
    except Exception as e:
        print(f"Error processing order: {e}")


if __name__ == "__main__":
    while True:
        new_orders = fetch_new_orders()
        if new_orders:
            for order in new_orders:
                process_order(order)
        else:
            print("No new orders to process.")
        # poll every 5 seconds
        time.sleep(5)
