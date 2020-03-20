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
import json

if __name__ == "__main__":

        # Create Spark Context to Connect Spark Cluster
    spark = SparkSession \
        .builder \
        .appName("My-App") \
        .getOrCreate()

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "tweepy-test") \
        .load() \
        .select(
            from_avro($"key", "t-key", schemaRegistryURL).as("key"),
            from_avro($"value", "t-value", schemaRegistryURL).as("value"))

    # .option("startingOffsets", """{"subscribe":{"0":23,"1":-2},"topic2":{"0":-2}}""") \

    # Set the Batch Interval is 10 sec of Streaming Context
    #ssc = StreamingContext(sc, 10)

    # Create Kafka Stream to Consume Data Comes From Twitter Topic
    # localhost:2181 = Default Zookeeper Consumer Address
    # kafkaStream = KafkaUtils.createStream(
    #    ssc, zkQuorum='localhost:2181', groupId='spark-streaming', topics={'tweepy-test': 1})

    # kafkaDStream = KafkaUtils.createDirectStream(
    #     ssc, ['tweepy-test'], {"metadata.broker.list": "localhost:9092"})
    # # Parse Twitter Data as json
    # parsed = kafkaDStream.map(lambda v: json.loads(v[1]))

    # # Count the number of tweets per User
    # user_counts = parsed.map(lambda tweet: (
    #     tweet['user']["screen_name"], 1)).reduceByKey(lambda x, y: x + y)

    # # Print the User tweet counts
    # user_counts.pprint()

    # # Start Execution of Streams
    # ssc.start()
    # ssc.awaitTermination()
