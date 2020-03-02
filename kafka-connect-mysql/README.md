# Kafka Connect with MySQL

Slighty modified from Confluent's example. Only version is updated.

- confluent platform docker version 5.4.0
- mysql version 8.0.19

## Prerequisites

- Docker
- Docker Compose
- curl
- **Docker-Machine**  
  Docker for mac is not native as Linux.  
  Weird network behavior may occur.

## (Mac) Start Docker-Machine

```bash
# if using docker-machine
docker-machine create --driver virtualbox --virtualbox-memory 6000 confluent
eval $(docker-machine env confluent)
```

## Download MySQL JDBC Driver

Make sure MySQL-JDBC version suit MySQL version.

```bash
$ docker exec quickstart-mysql mysql --version
mysql  Ver 8.0.19 for Linux on x86_64 (MySQL Community Server - GPL)
```

```bash
# if using docker-machine
docker-machine >/dev/null 2>&1 && docker-machine ssh confluent
```

```bash
# /tmp/quickstart/jars/mysql-connector-java-8.0.19.jar is mounted to container "connect" through docker-compose volume
sudo -s
curl -k -SL \
"http://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-8.0.19.tar.gz" | \
tar -xzf - -C /tmp/quickstart/jars \
--strip-components=1 \
mysql-connector-java-8.0.19/mysql-connector-java-8.0.19.jar
```

```bash
root@confluent:/home/docker# ls -la /tmp/quickstart/jars/
-rw-r--r--    1 root     root       2356711 Dec  4 11:44 /tmp/quickstart/jars/mysql-connector-java-8.0.19.jar
```

MySQL-JDBC can be found here

- [MySQL Engineering Blogs](https://dev.mysql.com/downloads/connector/j/)
- [mvnrepository](https://mvnrepository.com/artifact/mysql/mysql-connector-java/8.0.19)

## Start Docker Compose

```bash
docker-compose up -d
```

## Dump some data into MySQL

```bash
docker exec -it quickstart-mysql mysql -u confluent -pconfluent
```

```sql
CREATE DATABASE IF NOT EXISTS connect_test;
USE connect_test;

DROP TABLE IF EXISTS test;

CREATE TABLE IF NOT EXISTS test (
  id serial NOT NULL PRIMARY KEY,
  name varchar(100),
  email varchar(200),
  department varchar(200),
  modified timestamp default CURRENT_TIMESTAMP NOT NULL,
  INDEX `modified_index` (`modified`)
);

INSERT INTO test (name, email, department) VALUES ('alice', 'alice@abc.com', 'engineering');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
exit;
```

## Source Connector

### Add source connector

Either API or Web UI(Confluent Platform) will acheive the goal.

```bash
# You docker network name
export CONNECT_NET="kafka-connect-mysql_default"
```

```bash
# To call the API
docker run \
    --net="${CONNECT_NET}" \
    --rm curlimages/curl:7.68.0 -X \
    POST -H "Content-Type: application/json" \
    --data '{ "name": "quickstart-jdbc-source", "config": { "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector", "tasks.max": 1, "connection.url": "jdbc:mysql://quickstart-mysql:3306/connect_test?user=root&password=confluent", "mode": "incrementing", "incrementing.column.name": "id", "timestamp.column.name": "modified", "topic.prefix": "quickstart-jdbc-", "poll.interval.ms": 1000 } }' \
    http://connect:8083/connectors
```

```bash
# To open Confluent Platform web UI:
docker-machine >/dev/null 2>&1 && export CONNECT_HOST=$(docker-machine ip confluent) || export CONNECT_HOST="localhost"
open "http://${CONNECT_HOST}:9021/clusters"
```

### Status check (Source)

```bash
# Check connector status through API
docker run \
    --net="${CONNECT_NET}" \
    --rm \
    curlimages/curl:7.68.0 -s \
    -X GET http://connect:8083/connectors/quickstart-jdbc-source/status

# Check if new topic is created
docker run \
    --net="${CONNECT_NET}" \
    --rm \
    confluentinc/cp-kafka:5.4.0 \
    kafka-topics --describe \
    --zookeeper zookeeper:2181

# Consume through kafka-avro-console-consumer
docker exec schema-registry \
    kafka-avro-console-consumer \
    --bootstrap-server broker:29092 \
    --topic quickstart-jdbc-test \
    --from-beginning \
    --max-messages 10

```

## Sink Connector

### Add sink connector

```bash
# To call the API
docker run \
    --net="${CONNECT_NET}" \
    --rm \
    curlimages/curl:7.68.0 \
    -X POST \
    -H "Content-Type: application/json" \
    --data '{"name": "quickstart-avro-file-sink", "config": {"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector", "tasks.max":"1", "topics":"quickstart-jdbc-test", "file": "/tmp/quickstart/jdbc-output.txt"}}' \
    http://connect:8083/connectors
```

### Status check (Sink)

```bash
# Check connector status through API
docker run \
    --net="${CONNECT_NET}" \
    --rm \
    curlimages/curl:7.68.0 \
    -s -X GET http://connect:8083/connectors/quickstart-avro-file-sink/status
```

## DEBUG

Error messege

```json
{
  "error_code": 400,
  "message": "Connector configuration is invalid and contains the following 2 error(s):\nInvalid value java.sql.SQLException: No suitable driver found for jdbc:mysql://quickstart-mysql:3306/connect_test?user=root&password=confluent for configuration Couldn't open connection to jdbc:mysql://quickstart-mysql:3306/connect_test?user=root&password=confluent\nInvalid value java.sql.SQLException: No suitable driver found for jdbc:mysql://quickstart-mysql:3306/connect_test?user=root&password=confluent for configuration Couldn't open connection to jdbc:mysql://quickstart-mysql:3306/connect_test?user=root&password=confluent\nYou can also find the above list of errors at the endpoint `/{connectorType}/config/validate`"
}
```

[Explaination](https://www.confluent.io/blog/kafka-connect-deep-dive-jdbc-source-connector/#no-suitable-driver-found)

Uncomment the CONNECT_LOG4J_ROOT_LOGLEVEL in docker-compose connect container to check if mysql-jdbc is correctly loaded.

```bash
CONNECT_LOG4J_ROOT_LOGLEVEL: "DEBUG"
```

```bash
# restart docker-compose
docker-compose stop ; docker-compose up -d

# check the logs
docker logs -f connect | grep -i "mysql"
```

## Results

```bash
# if using docker-machine
docker-machine >/dev/null 2>&1 && docker-machine ssh confluent
```

```bash
cat /tmp/quickstart/file/jdbc-output.txt
```

Should see the data from MySQL

## References

- <https://docs.confluent.io/5.0.0/installation/docker/docs/installation/connect-avro-jdbc.html>
- <https://www.confluent.io/blog/kafka-connect-deep-dive-jdbc-source-connector/#no-suitable-driver-found>
- <https://rmoff.net/post/kafka-connect-change-log-level-and-write-log-to-file/>
