# Kafka Connect with MySQL

Confluent platform docker version 5.4.0.

## Table of content

- [Kafka Connect with MySQL](#kafka-connect-with-mysql)
  - [Table of content](#table-of-content)
  - [Prerequisites](#prerequisites)
  - [Install](#install)
  - [RUN](#run)
    - [Plaintext Producer + Consumer (without schema-registry)](#plaintext-producer--consumer-without-schema-registry)
    - [Avro Producer + Consumer (with schema-registry)](#avro-producer--consumer-with-schema-registry)
  - [References](#references)

## Prerequisites

- Docker + Docker Compose
- tweepy

## Install

```bash
# Start Kafka cluster
docker-compose up -d
```

## RUN

### Plaintext Producer + Consumer (without schema-registry)

```bash
# Start producer
python tweet-producer.py

# Start pyspark stream processor
PYSPARK_PYTHON=python3 spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.2.0 kafka-pyspark.py
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
