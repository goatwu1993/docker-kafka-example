"""
RUNNING PROGRAM;
1-Start Apache Kafka
./kafka/kafka_2.11-0.11.0.0/bin/kafka-server-start.sh ./kafka/kafka_2.11-0.11.0.0/config/server.properties
2-Run kafka_push_listener.py (Start Producer)
ipython >> run kafka_push_listener.py
3-Run kafka_twitter_spark_streaming.py (Start Consumer)
PYSPARK_PYTHON=python3 bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.2.0 ~/Documents/kafka_twitter_spark_streaming.py
"""

from pyspark.sql import SparkSession, SQLContext, DataFrame
import pyspark.sql.functions as psf
import os

# SUPER AWESOME confluent schema-registry wrapper
# Original credit:
# https://stackoverflow.com/a/55786881/9648709


def expand_avro(spark_context, sql_context, data_frame, schema_registry_url, topic):
    j = spark_context._gateway.jvm
    dataframe_deserializer = j.za.co.absa.abris.avro.AvroSerDe.DataframeDeserializer(
        data_frame._jdf)
    naming_strategy = getattr(
        getattr(j.za.co.absa.abris.avro.read.confluent.SchemaManager,
                "SchemaStorageNamingStrategies$"), "MODULE$").TOPIC_NAME()
    conf = getattr(
        getattr(j.scala.collection.immutable.Map, "EmptyMap$"), "MODULE$")
    conf = getattr(conf, "$plus")(j.scala.Tuple2(
        "schema.registry.url", schema_registry_url))
    conf = getattr(conf, "$plus")(
        j.scala.Tuple2("schema.registry.topic", topic))
    conf = getattr(conf, "$plus")(
        j.scala.Tuple2("value.schema.id", "latest"))
    conf = getattr(conf, "$plus")(j.scala.Tuple2(
        "value.schema.naming.strategy", naming_strategy))
    schema_path = j.scala.Option.apply(None)
    conf = j.scala.Option.apply(conf)
    policy = getattr(j.za.co.absa.abris.avro.schemas.policy.SchemaRetentionPolicies,
                     "RETAIN_SELECTED_COLUMN_ONLY$")()
    data_frame = dataframe_deserializer.fromConfluentAvro(
        "value", schema_path, conf, policy)
    data_frame = DataFrame(data_frame, sql_context)
    return data_frame


if __name__ == "__main__":

    os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages ' \
        'org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.4,' \
        'org.apache.spark:spark-avro_2.11:2.4.1,' \
        'za.co.absa:abris_2.11:2.2.2 ' \
        '--repositories https://packages.confluent.io/maven/ ' \
        'pyspark-shell'

    spark = SparkSession \
        .builder \
        .appName("My-App") \
        .getOrCreate()
    sc = spark.sparkContext
    sql = SQLContext(sc, spark)

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "tweepy-avro-test") \
        .load()

    # Expand df with avro
    df_rs = expand_avro(
        sc, sql, df, 'http://localhost:8081', 'tweepy-avro-test')

    df_rs.printSchema()
    df_rs.writeStream.format("console").start()
    spark.streams.awaitAnyTermination()
