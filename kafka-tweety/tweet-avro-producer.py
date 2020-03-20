from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import twitter_config
import twitter_schema
import json

# TWITTER API CONFIGURATIONS
consumer_key = twitter_config.consumer_key
consumer_secret = twitter_config.consumer_secret
access_token = twitter_config.access_token
access_secret = twitter_config.access_secret
# TWITTER API AUTH
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)


class TweetAvroProducer(StreamListener):
    def __init__(self,
                 api=None,
                 producer: AvroProducer = None,
                 value_fields: list = []):
        super().__init__(api=api)
        self.producer: AvroProducer = producer
        self.value_fields: list = value_fields

    def on_data(self, data):
        if (self.producer == None):
            return False
        json_value = self.value_transformer(data)
        print(json_value)
        self.producer.poll(0)
        self.producer.produce(
            topic='tweepy-avro-test',
            key={"name": "Key"},
            value=json_value
        )
        return True

    def on_error(self, status):
        print(status)

    def value_transformer(self, data):
        json_tweet = json.loads(data)
        json_tweet_important = {
            k: json_tweet[k] for k in self.value_fields
        }
        json_tweet_important['text'] = \
            json_tweet_important['text'].\
            replace("'", "").\
            replace("\"", "").\
            replace("\n", "")
        return json_tweet_important


def delivery_report(err, msg):
    """
    Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush().
    """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(
            msg.topic(), msg.partition()))


if __name__ == "__main__":
    # Kafka Producer Settings
    bootstrap_servers: str = "localhost:9092"
    schema_registry_url: str = "http://localhost:8081"
    value_schema = avro.loads(twitter_schema.value_schema_str)
    key_schema = avro.loads(twitter_schema.key_schema_str)

    # Init a AvroProducer for TweetAvroProducer
    my_avro_producer = AvroProducer({
        'bootstrap.servers': bootstrap_servers,
        'on_delivery': delivery_report,
        'schema.registry.url': schema_registry_url},
        default_key_schema=key_schema,
        default_value_schema=value_schema)

    # TweetAvroProducer Settings
    # value_fields should match value_schema_str
    # TODO: value_fields is nasty transformed from value_schema and only work in this case

    my_tweet_producer = TweetAvroProducer(
        producer=my_avro_producer,
        value_fields=[x['name'] for x in value_schema.to_json()["fields"]]
    )
    # Handles Twitter authetification and the connection to Twitter Streaming API
    stream = Stream(auth,  my_tweet_producer)
    tracklist = ['#conovirus', '#COVID-19']
    stream.filter(track=tracklist)
