import json

from confluent_kafka import Consumer, KafkaException

KAFKA_BROKER = "localhost:9092"
TOPICS = ["api_errors","api_requests","api_responses"]
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
        print(len(data))

        if data.get("event")=="API Request":
            print(data.get("endpoint"))
            print(data.get("method"))
        elif data.get("event")=="API Response":
            print(data.get("endpoint"))
            print(data.get("status_code"))
            response=data.get("response")
            print(response["response_time"])
        elif data.get("event")=="API Error":
            print(data.get("endpoint"))
            print(data.get("error"))

        # order_data = data.get("data", {})
        # print("Order data:")
        # print(json.dumps(order_data, indent=2))

        # print(json.dumps(data, indent=2))

except KeyboardInterrupt:
    print("\nStopping consumer...")
finally:
    consumer.close()


# Received message from api_requests:
# {
#   "event": "API Request",
#   "endpoint": "http://localhost:3000/orders",
#   "method": "POST",
#   "data": {
#     "userId": 4,
#     "productId": 3,
#     "quantity": 1,
#     "date": "2025-04-05",
#     "processed": false
#   }
# }


# Received message from api_responses:
# {
#   "event": "API Response",
#   "endpoint": "http://localhost:3000/orders",
#   "status_code": 201,
#   "response": {
#     "response_time": 0.0231,
#     "id": "e0ad",
#     "userId": 3,
#     "productId": 1,
#     "quantity": 4,
#     "date": "2025-04-05",
#     "processed": false
#   }
# }


# Received message from api_errors:
# {
#   "event": "API Error",
#   "endpoint": "http://localhost:3000/orders",
#   "error": "Not Found"
# }