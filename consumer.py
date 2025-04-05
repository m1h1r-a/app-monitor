import json

from confluent_kafka import Consumer, KafkaException

KAFKA_BROKER = "localhost:9092"
TOPICS = ["api_errors", "api_requests", "api_responses"]
GROUP_ID = "log-consumer-group"


consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
    }
)


consumer.subscribe(TOPICS)

print(f"🔍 Listening to Kafka topics: {TOPICS}...")

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

except KeyboardInterrupt:
    print("\nStopping consumer...")
finally:
    consumer.close()
