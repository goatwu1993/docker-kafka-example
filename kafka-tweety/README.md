# Kafka Integrate with Spark Structured Streaming using Python/PySpark

Kafka: Confluent platform docker version 5.4.0.
Spark: 2.4.5

## Table of content

- [Kafka Integrate with Spark Structured Streaming using Python/PySpark](#kafka-integrate-with-spark-structured-streaming-using-pythonpyspark)
  - [Table of content](#table-of-content)
  - [Prerequisites](#prerequisites)
  - [Environment](#environment)
  - [Run](#run)
    - [Json Producer + Consumer (Plaintext, without schema-registry)](#json-producer--consumer-plaintext-without-schema-registry)
    - [Avro Producer + Consumer (with schema-registry)](#avro-producer--consumer-with-schema-registry)
  - [Stop](#stop)
  - [References](#references)

## Prerequisites

- Docker + Docker Compose
- Python Package
  - Producer
    - confluent-kafka-python
    - tweepy
  - Consumer
    - pyspark

## Environment

```bash
# Start Kafka cluster
docker-compose up -d
kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic tweepy-json-test
kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic tweepy-avro-test
kafka-topics --describe --bootstrap-server localhost:9092 --topic 'tweepy.*'
```

## Run

### Json Producer + Consumer (Plaintext, without schema-registry)

```bash
# Start producer
python tweet-json-producer.py>/dev/null 2>&1 &
# Start pyspark stream processor
python spark-json-consumer.py
```

### Avro Producer + Consumer (with schema-registry)

```bash
# Start producer
python tweet-avro-producer.py>/dev/null 2>&1 &

# Start pyspark stream processor
python spark-avro-consumer.py
```

## Stop

```bash
pkill tweet-json-producer.py
pkill spark-json-consumer.py
pkill tweet-avro-producer.py
pkill spark-avro-consumer.py
```

## References

- <https://github.com/kaantas/kafka-twitter-spark-streaming/blob/master/kafka_push_listener.py>
- <https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html>
- <https://stackoverflow.com/questions/54701460/how-to-parse-a-json-string-column-in-pysparks-datastreamreader-and-create-a-dat>
- <https://codertw.com/程式語言/356804/>
- <https://github.com/apache/spark/pull/23797>
- <https://stackoverflow.com/a/55786881/9648709>
