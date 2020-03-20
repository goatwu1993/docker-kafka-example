# Kafka Connect with MySQL

Confluent platform docker version 5.4.0 + MySQL version 8.0.19

## Table of content

- [Kafka Connect with MySQL](#kafka-connect-with-mysql)
  - [Table of content](#table-of-content)
  - [Prerequisites](#prerequisites)
  - [Install](#install)
  - [Run](#run)
  - [Debug](#debug)
  - [Results](#results)
  - [References](#references)

## Prerequisites

- Docker + Docker Compose
- curl

## Install

MySQL-JDBC (MySQL-JDBC & MySQL should be **version-compatible**)

```bash
## Download JDBC
chmod 755 curl_jdbc.sh
./curl_jdbc.sh
```

## Run

```bash
# Enter this directory
export CONNECT_NET="kafka-connect-mysql_default"

## Start containers
docker-compose up --build

# Add Source Connector
docker run --net="${CONNECT_NET}" --rm curlimages/curl:7.68.0 -X POST -s -H "Content-Type: application/json" --data '{ "name": "quickstart-jdbc-source", "config": { "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector", "tasks.max": 1, "connection.url": "jdbc:mysql://quickstart-mysql:3306/connect_test?user=root&password=confluent", "mode": "incrementing", "incrementing.column.name": "id", "timestamp.column.name": "modified", "topic.prefix": "quickstart-jdbc-", "poll.interval.ms": 1000 } }' http://connect:8083/connectors

# Results 1
docker exec schema-registry kafka-avro-console-consumer --bootstrap-server broker:29092 --topic quickstart-jdbc-test --from-beginning --property print.key=true --max-messages 10 | grep -e "^null"

# Add Sink Connector
docker run --net="${CONNECT_NET}" --rm curlimages/curl:7.68.0 -s -X POST -H "Content-Type: application/json" --data '{"name": "quickstart-avro-file-sink", "config": {"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector", "tasks.max":"1", "topics":"quickstart-jdbc-test", "file": "/tmp/quickstart/jdbc-output.txt"}}' http://connect:8083/connectors

# Results 2
docker exec connect cat /tmp/quickstart/jdbc-output.txt
```

## Debug

Make sure MySQL-JDBC JAR file is correctly mounted to container. Then higher the logging level from docker-compose.yml and observe the logs from connector

## Results

The file should be dump into /tmp/quickstart/jdbc-output.txt.

## References

- <https://docs.confluent.io/5.0.0/installation/docker/docs/installation/connect-avro-jdbc.html>
- <https://www.confluent.io/blog/kafka-connect-deep-dive-jdbc-source-connector/#no-suitable-driver-found>
- <https://rmoff.net/post/kafka-connect-change-log-level-and-write-log-to-file/>
- <https://stackoverflow.com/questions/25503412/how-do-i-know-when-my-docker-mysql-container-is-up-and-mysql-is-ready-for-taking>
- <https://dev.mysql.com/downloads/connector/j/>
- <https://mvnrepository.com/artifact/mysql/mysql-connector-java/8.0.19>
