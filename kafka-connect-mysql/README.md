# Kafka Connect with MySQL

Slighty modified from Confluent's example. Only version is updated.

- confluent platform docker version 5.4.0
- mysql version 8.0.19

Note that docker-compose.yml is slightly modified from [cp-all-in-one](https://github.com/confluentinc/cp-docker-images/blob/5.3.0-post/examples/cp-all-in-one/docker-compose.yml) in order to be easily understood.

The docker images is **NOT Size-Mininized**.

## Prerequisites

- Docker
- Docker Compose
- curl
- **Docker-Machine**  
  Docker for mac is not as native as Linux. Weird network behavior may occur.  
  Better use docker-machine to avoid it.

## (Mac) Start Docker-Machine

## Download MySQL JDBC Driver

It is important to make sure the **version of MySQL-JDBC** match **the version of MySQL**.

- [MySQL Engineering Blogs](https://dev.mysql.com/downloads/connector/j/)
- [mvnrepository](https://mvnrepository.com/artifact/mysql/mysql-connector-java/8.0.19)

## Start Docker Compose

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

- url: http://connect:8083/connectors
- header:

  ```json
  "Content-Type: application/json"
  ```

- data:

  ```json
  {
    "name": "quickstart-jdbc-source",
    "config": {
      "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
      "tasks.max": 1,
      "connection.url": "jdbc:mysql://quickstart-mysql:3306/connect_test?user=root&password=confluent",
      "mode": "incrementing",
      "incrementing.column.name": "id",
      "timestamp.column.name": "modified",
      "topic.prefix": "quickstart-jdbc-",
      "poll.interval.ms": 1000
    }
  }
  ```

### If error message is received

Make sure MySQL-JDBC JAR file is correctly mounted to container. Then higher the logging level from docker-compose.yml and observe the logs from connector

## Sink Connector

- url: http://connect:8083/connectors
- header:

  ```json
  "Content-Type: application/json"
  ```

- data

  ```json
  {
    "name": "quickstart-avro-file-sink",
    "config": {
      "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
      "tasks.max": "1",
      "topics": "quickstart-jdbc-test",
      "file": "/tmp/quickstart/jdbc-output.txt"
    }
  }
  ```

## Results

The file should be dump into docker-machine host.

## References

- <https://docs.confluent.io/5.0.0/installation/docker/docs/installation/connect-avro-jdbc.html>
- <https://www.confluent.io/blog/kafka-connect-deep-dive-jdbc-source-connector/#no-suitable-driver-found>
- <https://rmoff.net/post/kafka-connect-change-log-level-and-write-log-to-file/>
- <https://stackoverflow.com/questions/25503412/how-do-i-know-when-my-docker-mysql-container-is-up-and-mysql-is-ready-for-taking>
