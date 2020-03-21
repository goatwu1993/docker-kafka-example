"""
RUNNING PROGRAM;
1-Start Apache Kafka
./kafka/kafka_2.11-0.11.0.0/bin/kafka-server-start.sh ./kafka/kafka_2.11-0.11.0.0/config/server.properties
2-Run kafka_push_listener.py (Start Producer)
ipython >> run kafka_push_listener.py
3-Run kafka_twitter_spark_streaming.py (Start Consumer)
PYSPARK_PYTHON=python3 bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.2.0 ~/Documents/kafka_twitter_spark_streaming.py
"""

from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import pyspark.sql.functions as psf
from pyspark.sql.types import StructType, StructField, StringType, DateType, IntegerType, BooleanType, LongType

import json

import os

if __name__ == "__main__":

    os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.4 pyspark-shell'

    schema = StructType().\
        add("created_at", StringType()).\
        add("id", LongType()).\
        add("id_str", StringType()).\
        add("text", StringType()).\
        add("retweet_count", IntegerType()).\
        add("favorite_count", IntegerType()).\
        add("favorited", BooleanType()).\
        add("retweeted", BooleanType()).\
        add("lang", StringType())

    spark = SparkSession \
        .builder \
        .appName("My-App") \
        .getOrCreate()

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "tweepy-test") \
        .load()


    df_rs = df.\
        selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)").\
        select(psf.col("key").cast("string"), psf.from_json(
            psf.col("value").cast("string"), schema).alias("data"))

    df_rs.printSchema()
    df_flattened = df_rs.selectExpr("key", "data.*")

    df_flattened.writeStream.\
        format("console").\
        start()

    spark.streams.awaitAnyTermination()
