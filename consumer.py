import json
import pymysql
from datetime import datetime, timedelta
from confluent_kafka import Consumer, KafkaException

KAFKA_BROKER = "localhost:9092"
TOPICS = ["api_errors","api_requests","api_responses"]
GROUP_ID = "log-consumer-group"

# MySQL Connection
db = pymysql.connect(
    host="localhost",
    port=3307,
    user="root",
    password="password",
    database="log_monitoring",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
    }
)


consumer.subscribe(TOPICS)

print(f"🔍 Listening to Kafka topics: {TOPICS}...")

def insert_log(log):
    try:
        with db.cursor() as cursor:
            query = """
            INSERT INTO logs (
                endpoint, method, status_code, response, response_time,
                error, log_level, metadata, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                log['endpoint'],
                log['method'],
                log['status_code'],
                log['response'],
                log['response_time'],
                log['error'],
                log['log_level'],
                None,
                log['timestamp']
            ))
    except Exception as e:
        print(f"MySQL insert error: {e}")

def build_log(endpoint,method,status_code,response,response_time,error,log_level,timestamp):
    log={
        "endpoint":endpoint,
        "method":method,
        "status_code":status_code,
        "response":response,
        "response_time":response_time,
        "error":error,
        "log_level":log_level,
        "timestamp":timestamp
    }
    return log

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
            log=build_log(data.get("endpoint"),data.get("method"),0,0,0.0,None,"Request",datetime.now())
            insert_log(log)

        elif data.get("event")=="API Response":
            print(data.get("endpoint"))
            print(data.get("status_code"))
            response=data.get("response")
            print(response["response_time"])
            response_time = response.get("response_time", 0.0)
            log=build_log(data.get("endpoint"),"N/A",data.get("status_code"),1,response_time,None,"Response",datetime.now())
            insert_log(log)

        elif data.get("event")=="API Error":
            print(data.get("endpoint"))
            print(data.get("error"))
            log=build_log(data.get("endpoint"),"N/A",data.get("status_code"),0,0.0,data.get("error"),"Error",datetime.now())
            insert_log(log)

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