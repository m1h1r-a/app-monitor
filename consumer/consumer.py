import json
from confluent_kafka import Consumer, KafkaException

# Kafka configuration
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "orders"

consumer_conf = {
    "bootstrap.servers": KAFKA_BROKER,
    "group.id": "order_group",          # Consumer group ID for managing offsets
    "auto.offset.reset": "earliest"       # Start from the beginning if no offset is committed
}

# Create a Consumer instance
consumer = Consumer(consumer_conf)

# Subscribe to the "orders" topic
consumer.subscribe([KAFKA_TOPIC])
print("Consumer subscribed to topic 'orders'.")

try:
    while True:
        # Poll for messages (1 second timeout)
        msg = consumer.poll(1.0)
        if msg is None:
            continue  # No message available yet
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        # Process the message
        try:
            order = json.loads(msg.value().decode("utf-8"))
            print(f"Consumed order: {order}")
        except Exception as e:
            print(f"Error processing message: {e}")
except KeyboardInterrupt:
    print("Consumer interrupted by user.")
finally:
    # Close the consumer cleanly
    consumer.close()
    print("Consumer closed.")
