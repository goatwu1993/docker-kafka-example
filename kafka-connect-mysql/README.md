
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
docker-machine create --driver virtualbox --virtualbox-memory 6000 confluent || echo "continue"
```

    Docker machine "confluent" already exists
    continue



```bash
docker-machine start confluent || echo "continue"
```

    Starting "confluent"...
    Machine "confluent" is already running.
    continue



```bash
eval $(docker-machine env confluent)
```

## Download MySQL JDBC Driver

Please make sure MySQL-JDBC version suit MySQL version.


```bash
docker-compose stop ; docker-compose rm -f
```

    Stopping control-center   ... 
    Stopping quickstart-mysql ... 
    Stopping connect          ... 
    Stopping schema-registry  ... 
    Stopping broker           ... 
    Stopping zookeeper        ... 
    [1BGoing to remove control-center, quickstart-mysql, connect, schema-registry, broker, zookeeper
    Removing control-center   ... 
    Removing quickstart-mysql ... 
    Removing connect          ... 
    Removing schema-registry  ... 
    Removing broker           ... 
    Removing zookeeper        ... 
    [6Bving control-center   ... [32mdone[0m


```bash
docker run --rm mysql --version
```

    /usr/sbin/mysqld  Ver 8.0.19 for Linux on x86_64 (MySQL Community Server - GPL)



```bash
# if using docker-machine
docker-machine ssh confluent -- \
"""
sudo mkdir -p /tmp/quickstart/jars;
sudo curl -k \
    -s \
    -SL \
    \"http://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-8.0.19.tar.gz\" |
    sudo tar -xzf - -C \
        /tmp/quickstart/jars \
        --strip-components=1 \
        mysql-connector-java-8.0.19/mysql-connector-java-8.0.19.jar;
ls -la /tmp/quickstart/jars
"""
```

    total 2312
    drwxr-xr-x    2 root     root          4096 Mar  2 20:42 .
    drwxr-xr-x    4 root     root          4096 Mar  2 18:20 ..
    -rw-r--r--    1 root     root       2356711 Dec  4 11:44 mysql-connector-java-8.0.19.jar


MySQL-JDBC can be found here

- [MySQL Engineering Blogs](https://dev.mysql.com/downloads/connector/j/)
- [mvnrepository](https://mvnrepository.com/artifact/mysql/mysql-connector-java/8.0.19)

## Start Docker Compose


```bash
docker-compose up -d
```

    Creating zookeeper ... 
    [1BCreating broker    ... mdone[0m
    [1BCreating schema-registry ... [0m
    [1BCreating connect         ... mdone[0m
    [1BCreating quickstart-mysql ... done[0m
    Creating control-center   ... 
    [1Bting control-center   ... [32mdone[0m

## Dump some data into MySQL

MySQL may take some time to load


```bash
# Nasty script to wait for mysql ready
while ! docker exec quickstart-mysql mysql --user=confluent --password=confluent -e "SELECT 1" >/dev/null 2>&1; do
 sleep 1
done
```


```bash
docker exec -i quickstart-mysql mysql -u confluent -pconfluent <<< """
CREATE DATABASE IF NOT EXISTS connect_test;
USE connect_test;

DROP TABLE IF EXISTS test;

CREATE TABLE IF NOT EXISTS test (
  id serial NOT NULL PRIMARY KEY,
  name varchar(100),
  email varchar(200),
  department varchar(200),
  modified timestamp default CURRENT_TIMESTAMP NOT NULL,
  INDEX \`modified_index\` (\`modified\`)
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
SELECT * FROM test;
"""
```

    mysql: [Warning] Using a password on the command line interface can be insecure.
    id	name	email	department	modified
    1	alice	alice@abc.com	engineering	2020-03-02 20:44:27
    2	bob	bob@abc.com	sales	2020-03-02 20:44:27
    3	bob	bob@abc.com	sales	2020-03-02 20:44:27
    4	bob	bob@abc.com	sales	2020-03-02 20:44:27
    5	bob	bob@abc.com	sales	2020-03-02 20:44:27
    6	bob	bob@abc.com	sales	2020-03-02 20:44:27
    7	bob	bob@abc.com	sales	2020-03-02 20:44:27
    8	bob	bob@abc.com	sales	2020-03-02 20:44:27
    9	bob	bob@abc.com	sales	2020-03-02 20:44:27
    10	bob	bob@abc.com	sales	2020-03-02 20:44:27


## Source Connector

### Add source connector

Either API or Web UI(Confluent Platform) will acheive the goal.


```bash
export CONNECT_NET="kafka-connect-mysql_default"
```

The kafka-connect container may take a while until REST staart up.


```bash
# Call the API of connect
docker run \
    --net="${CONNECT_NET}" \
    --rm curlimages/curl:7.68.0 \
    -X POST \
    -s \
    -H "Content-Type: application/json" \
    --data '{ "name": "quickstart-jdbc-source", "config": { "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector", "tasks.max": 1, "connection.url": "jdbc:mysql://quickstart-mysql:3306/connect_test?user=root&password=confluent", "mode": "incrementing", "incrementing.column.name": "id", "timestamp.column.name": "modified", "topic.prefix": "quickstart-jdbc-", "poll.interval.ms": 1000 } }' \
    http://connect:8083/connectors
```

    {"error_code":409,"message":"Connector quickstart-jdbc-source already exists"}


```bash
# Check if new topic is created
docker run \
    --net="${CONNECT_NET}" \
    --rm \
    confluentinc/cp-kafka:5.4.0 \
    kafka-topics --describe \
    --zookeeper zookeeper:2181 \
    --topic quickstart-jdbc-test
```

    Topic: quickstart-jdbc-test	PartitionCount: 1	ReplicationFactor: 1	Configs: 
    	Topic: quickstart-jdbc-test	Partition: 0	Leader: 1	Replicas: 1	Isr: 1



```bash
docker exec schema-registry \
    kafka-avro-console-consumer \
    --bootstrap-server broker:29092 \
    --topic quickstart-jdbc-test \
    --from-beginning \
    --property print.key=true \
    --max-messages 10 | \
    grep -e "^null"
```

    null	{"id":1,"name":{"string":"alice"},"email":{"string":"alice@abc.com"},"department":{"string":"engineering"},"modified":1583181867000}
    null	{"id":2,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583181867000}
    null	{"id":3,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583181867000}
    null	{"id":4,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583181867000}
    null	{"id":5,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583181867000}
    null	{"id":6,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583181867000}
    null	{"id":7,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583181867000}
    null	{"id":8,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583181867000}
    null	{"id":9,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583181867000}
    null	{"id":10,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583181867000}
    Processed a total of 10 messages


## Sink Connector

### Add sink connector


```bash
# Call the API of connect
docker run \
    --net="${CONNECT_NET}" \
    --rm \
    curlimages/curl:7.68.0 \
    -X POST \
    -H "Content-Type: application/json" \
    --data '{"name": "quickstart-avro-file-sink", "config": {"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector", "tasks.max":"1", "topics":"quickstart-jdbc-test", "file": "/tmp/quickstart/jdbc-output.txt"}}' \
    http://connect:8083/connectors
```

      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100   487  100   270  100   217    461    370 --:--:-- --:--:-- --:--:--   833
    {"name":"quickstart-avro-file-sink","config":{"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector","tasks.max":"1","topics":"quickstart-jdbc-test","file":"/tmp/quickstart/jdbc-output.txt","name":"quickstart-avro-file-sink"},"tasks":[],"type":"sink"}

### Status check (Sink)



```bash
# Check connector status through API
docker run \
    --net="${CONNECT_NET}" \
    --rm \
    curlimages/curl:7.68.0 \
    -s -X GET http://connect:8083/connectors/quickstart-avro-file-sink/status
```

    {"name":"quickstart-avro-file-sink","connector":{"state":"RUNNING","worker_id":"connect:8083"},"tasks":[],"type":"sink"}

## Results


```bash
# if using docker-machine
docker-machine >/dev/null 2>&1 && \
    docker-machine ssh confluent \
    cat /tmp/quickstart/file/jdbc-output.txt
```

    Struct{id=1,name=alice,email=alice@abc.com,department=engineering,modified=Mon Mar 02 20:38:25 UTC 2020}
    Struct{id=2,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 20:38:25 UTC 2020}
    Struct{id=3,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 20:38:25 UTC 2020}
    Struct{id=4,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 20:38:25 UTC 2020}
    Struct{id=5,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 20:38:25 UTC 2020}
    Struct{id=6,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 20:38:25 UTC 2020}
    Struct{id=7,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 20:38:25 UTC 2020}
    Struct{id=8,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 20:38:25 UTC 2020}
    Struct{id=9,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 20:38:25 UTC 2020}
    Struct{id=10,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 20:38:25 UTC 2020}



```bash

```
