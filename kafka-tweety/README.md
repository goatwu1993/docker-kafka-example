# Kafka Integrate with Spark Structured Streaming using Python

Confluent platform docker version 5.4.0.

## Table of content

- [Kafka Integrate with Spark Structured Streaming using Python](#kafka-integrate-with-spark-structured-streaming-using-python)
  - [Table of content](#table-of-content)
  - [Prerequisites](#prerequisites)
  - [Environment](#environment)
  - [Run](#run)
    - [Plaintext Producer + Consumer (without schema-registry)](#plaintext-producer--consumer-without-schema-registry)
    - [Avro Producer + Consumer (with schema-registry)](#avro-producer--consumer-with-schema-registry)
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
```

## Run

### Plaintext Producer + Consumer (without schema-registry)

```bash
# Start producer
python tweet-producer.py

# Start pyspark stream processor
python kafka-pyspark.py
```

### Avro Producer + Consumer (with schema-registry)

```bash
# Start Avro producer
python tweet-avro-producer.py

# Test1
docker exec schema-registry kafka-avro-console-consumer --bootstrap-server broker:29092 --topic tweepy-avro-test --from-beginning --property print.key=true

# TODO: Java code with schema-registry

```

## References

- <https://github.com/kaantas/kafka-twitter-spark-streaming/blob/master/kafka_push_listener.py>
- <https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html>
- <https://stackoverflow.com/questions/54701460/how-to-parse-a-json-string-column-in-pysparks-datastreamreader-and-create-a-dat>
- <https://codertw.com/程式語言/356804/>
