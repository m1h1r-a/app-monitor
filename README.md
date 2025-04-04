# app-monitor

## run and test apache-kafka:
```bash

# start kafka container
docker run -d --name=kafka -p 9092:9092 apache/kafka

# producer:
docker exec -ti kafka /opt/kafka/bin/kafka-cluster.sh cluster-id --bootstrap-server :9092

# consumer:
docker exec -ti kafka /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server :9092 --topic demo
```


## Build from docker images:
```bash
# Start JSON Server
docker build -t json-server-app .   
docker run -d -p 3000:3000 --name json-server-container json-server-app

# Start Kafka Broker
docker run -d --name=kafka -p 9092:9092 apache/kafka
```

## Run Python Scripts Locally(Uncontainerized - In separate Terminals)
```bash
python simulate_requests.py
python producer.py
python consumer.py
```
