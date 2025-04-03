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
docker build -t json-server-app .   

docker build -t kafka-producer ./producer
docker build -t kafka-consumer ./consumer
docker build -t workload-simulator ./simulator
```

## Docker network creation:
```bash
docker network create app-monitor-net 

to check if it exists:
```

## Run docker containers for python scripts
```bash
docker run -d --name=producer --network=app-monitor-net kafka-producer
docker run -d --name=consumer --network=app-monitor-net kafka-consumer
docker run -d --name=simulator --network=app-monitor-net workload-simulator
```
