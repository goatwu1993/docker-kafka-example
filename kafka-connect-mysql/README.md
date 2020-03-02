
# Kafka Connect with MySQL

Slighty modified from Confluent's example. Only version is updated.

- confluent platform docker version 5.4.0
- mysql version 8.0.19

## Prerequisites

- Docker
- Docker Compose
- curl
- **Docker-Machine**  
  Docker for mac is not as native as Linux. Weird network behavior may occur.  
  Better use docker-machine to avoid it.

## (Mac) Start Docker-Machine


```bash
# if using docker-machine
if [ docker-machine >/dev/null 2>&1 ]
then
    docker-machine create --driver virtualbox --virtualbox-memory 6000 confluent
else
    echo "Docker is native on your system"
fi
echo "continue"
```

    Docker machine "confluent" already exists
    continue



```bash
docker-machine start confluent
echo "continue"
```

    Starting "confluent"...
    Machine "confluent" is already running.
    continue



```bash
if [ docker-machine >/dev/null 2>&1 ]
then
    eval $(docker-machine env confluent)
else
    echo "Docker is native on your system"
fi
```

## Download MySQL JDBC Driver

It is important to make sure the **version of MySQL-JDBC** match **the version of MySQL**.


```bash
docker-compose stop
echo
docker-compose rm -f
```

    Stopping control-center  ... 
    Stopping connect         ... 
    Stopping schema-registry ... 
    Stopping broker          ... 
    Stopping zookeeper       ... 
    [1Bping zookeeper       ... [32mdone[0m
    Going to remove control-center, quickstart-mysql, connect, schema-registry, broker, zookeeper
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
if [ docker-machine >/dev/null 2>&1 ]
then
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
else
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
fi
```

    total 2312
    drwxr-xr-x    2 root     root          4096 Mar  2 22:27 .
    drwxr-xr-x    4 root     root          4096 Mar  2 22:19 ..
    -rw-r--r--    1 root     root       2356711 Dec  4 11:44 mysql-connector-java-8.0.19.jar


### MySQL-JDBC

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
    [1BCreating control-center  ... mdone[0m
    Creating quickstart-mysql ... 
    [1Bting quickstart-mysql ... [32mdone[0m

## Insert data into MySQL

MySQL container may take a while until it can function.


```bash
# Nasty script to wait for mysql be ready
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
    1	alice	alice@abc.com	engineering	2020-03-02 22:29:15
    2	bob	bob@abc.com	sales	2020-03-02 22:29:15
    3	bob	bob@abc.com	sales	2020-03-02 22:29:15
    4	bob	bob@abc.com	sales	2020-03-02 22:29:15
    5	bob	bob@abc.com	sales	2020-03-02 22:29:15
    6	bob	bob@abc.com	sales	2020-03-02 22:29:15
    7	bob	bob@abc.com	sales	2020-03-02 22:29:15
    8	bob	bob@abc.com	sales	2020-03-02 22:29:15
    9	bob	bob@abc.com	sales	2020-03-02 22:29:15
    10	bob	bob@abc.com	sales	2020-03-02 22:29:15


## Source Connector

### Add source connector

Either API or Web UI(Confluent Platform) will acheive the goal.


```bash
export CONNECT_NET="kafka-connect-mysql_default"
```

We have to wait for Kafka Connect to totally start up.  

To speed up the process, remove some directory from **CONNECT_PLUGIN_PATH**

```bash
      #CONNECT_PLUGIN_PATH: "/usr/share/java,/usr/share/confluent-hub-components"
      CONNECT_PLUGIN_PATH: "\
        /usr/share/java/kafka,\
        /usr/share/confluent-hub-components,\
        /usr/share/java/kafka-connect-jdbc,\
        /etc/kafka-connect/jars"
```


```bash
while ! docker logs connect 2>&1 | grep -i "INFO Kafka Connect started" ; do
     sleep 1
done
```

    [2020-03-02 22:32:15,768] INFO Kafka Connect started (org.apache.kafka.connect.runtime.Connect)



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

    {"name":"quickstart-jdbc-source","config":{"connector.class":"io.confluent.connect.jdbc.JdbcSourceConnector","tasks.max":"1","connection.url":"jdbc:mysql://quickstart-mysql:3306/connect_test?user=root&password=confluent","mode":"incrementing","incrementing.column.name":"id","timestamp.column.name":"modified","topic.prefix":"quickstart-jdbc-","poll.interval.ms":"1000","name":"quickstart-jdbc-source"},"tasks":[],"type":"source"}

### If error message is received

Make sure MySQL-JDBC JAR file is correctly mounted to container.


```bash
docker exec connect env | grep -e "^CONNECT_PLUGIN_PATH"
```

    CONNECT_PLUGIN_PATH=/usr/share/java/kafka,/usr/share/confluent-hub-components,/usr/share/java/kafka-connect-jdbc,/etc/kafka-connect/jars



```bash
docker exec connect ls -la /etc/kafka-connect/jars
```

    total 2312
    drwxr-xr-x 2 root root    4096 Mar  2 22:27 .
    drwxrwxrwx 1 root root    4096 Mar  2 22:28 ..
    -rw-r--r-- 1 root root 2356711 Dec  4 11:44 mysql-connector-java-8.0.19.jar


Higher the logging level from docker-compose.yml and run again 

```bash
    #CONNECT_LOG4J_ROOT_LOGLEVEL: "DEBUG"
```

### Status Check


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

    null	{"id":1,"name":{"string":"alice"},"email":{"string":"alice@abc.com"},"department":{"string":"engineering"},"modified":1583188155000}
    null	{"id":2,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583188155000}
    null	{"id":3,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583188155000}
    null	{"id":4,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583188155000}
    null	{"id":5,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583188155000}
    null	{"id":6,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583188155000}
    null	{"id":7,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583188155000}
    null	{"id":8,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583188155000}
    null	{"id":9,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583188155000}
    null	{"id":10,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1583188155000}
    Processed a total of 10 messages


## Sink Connector

### Add sink connector


```bash
# Call the API of connect
docker run \
    --net="${CONNECT_NET}" \
    --rm \
    curlimages/curl:7.68.0 \
    -s -X POST \
    -H "Content-Type: application/json" \
    --data '{"name": "quickstart-avro-file-sink", "config": {"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector", "tasks.max":"1", "topics":"quickstart-jdbc-test", "file": "/tmp/quickstart/jdbc-output.txt"}}' \
    http://connect:8083/connectors
```

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

    {"name":"quickstart-avro-file-sink","connector":{"state":"RUNNING","worker_id":"connect:8083"},"tasks":[{"id":0,"state":"RUNNING","worker_id":"connect:8083"}],"type":"sink"}

## Results


```bash
# if using docker-machine
if [ docker-machine >/dev/null 2>&1 ]
then
    docker-machine ssh confluent -- cat /tmp/quickstart/file/jdbc-output.txt
else
    cat /tmp/quickstart/file/jdbc-output.txt
fi
```

    Struct{id=1,name=alice,email=alice@abc.com,department=engineering,modified=Mon Mar 02 22:29:15 UTC 2020}
    Struct{id=2,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 22:29:15 UTC 2020}
    Struct{id=3,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 22:29:15 UTC 2020}
    Struct{id=4,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 22:29:15 UTC 2020}
    Struct{id=5,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 22:29:15 UTC 2020}
    Struct{id=6,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 22:29:15 UTC 2020}
    Struct{id=7,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 22:29:15 UTC 2020}
    Struct{id=8,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 22:29:15 UTC 2020}
    Struct{id=9,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 22:29:15 UTC 2020}
    Struct{id=10,name=bob,email=bob@abc.com,department=sales,modified=Mon Mar 02 22:29:15 UTC 2020}



```bash
docker-compose stop
```

    Stopping control-center   ... 
    Stopping quickstart-mysql ... 
    Stopping connect          ... 
    Stopping schema-registry  ... 
    Stopping broker           ... 
    Stopping zookeeper        ... 
    [1Bping zookeeper        ... [32mdone[0m

## References
- <https://docs.confluent.io/5.0.0/installation/docker/docs/installation/connect-avro-jdbc.html>
- <https://www.confluent.io/blog/kafka-connect-deep-dive-jdbc-source-connector/#no-suitable-driver-found>
- <https://rmoff.net/post/kafka-connect-change-log-level-and-write-log-to-file/>
- <https://stackoverflow.com/questions/25503412/how-do-i-know-when-my-docker-mysql-container-is-up-and-mysql-is-ready-for-taking>


```bash

```
