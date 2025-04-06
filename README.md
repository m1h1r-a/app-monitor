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

## Pull and run mysql container
```bash
docker pull mysql:latest

# with volumes:
docker run --name mysql-container \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=log_monitoring \
  -p 3307:3306 \
  -v mysql_data:/var/lib/mysql \
  -v "$(pwd)"/init.sql:/docker-entrypoint-initdb.d/init.sql \
  -d mysql:latest


# open after container restart
docker run --name mysql-container \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=log_monitoring \
  -p 3307:3306 \
  -v mysql_data:/var/lib/mysql \
  -d mysql:latest

docker exec -it mysql-container mysql -u root -p
```
## Prometheus on Docker
```bash
#create container
docker run --name prometheus-container \
  -p 9090:9090 \
  -v "$(pwd)/prometheus.yml":/etc/prometheus/prometheus.yml \
  -v prometheus_data:/prometheus \
  -d prom/prometheus

#start conatiner
docker start prometheus-container

# view metrics on
http://localhost:9090
Try querying:
    api_requests_total
    api_responses_total
    api_errors_total
    api_response_time_seconds_bucket
```

## Dependencies to run consumer.py locally
```bash
pip install confluent_kafka
pip install pymysql
pip install cryptography
pip install prometheus_client
```
