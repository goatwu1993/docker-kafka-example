from confluent_kafka import Producer, avro
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


class TweetKafkaProducer(StreamListener):
    def __init__(self,
                 api=None,
                 producer: Producer = None,
                 value_fields: list = []):
        super().__init__(api=api)
        self.producer: Producer = producer
        self.value_fields: list = value_fields

    def on_data(self, data):
        if (self.producer == None):
            return False
        json_value = self.value_transformer(data)
        print(json_value)
        self.producer.poll(0)
        self.producer.produce(
            topic='tweepy-test',
            key=None,
            value=json_value.encode('utf-8')
        )
        return True

    def on_error(self, status):
        print(status)

    def value_transformer(self, data):
        json_tweet = json.loads(data)
        json_tweet_important = {
            k: json_tweet[k] for k in self.value_fields
        }
        # dump dict to valid json string using json.dumps
        rs_str = json.dumps(json_tweet_important)
        return rs_str


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
    # Kafka AvroProducer Settings
    bootstrap_servers: str = "localhost:9092"
    value_schema = avro.loads(twitter_schema.value_schema_str)

    # Init a AvroProducer for TweetKafkaProducer
    my_producer = Producer({
        'bootstrap.servers': bootstrap_servers,
        'on_delivery': delivery_report
    })

    # TweetKafkaProducer Settings
    # value_fields should match value_schema_str
    # TODO: value_fields is nastily transformed from value_schema and only work in this case

    my_tweet_producer = TweetKafkaProducer(
        producer=my_producer,
        value_fields=[x['name'] for x in value_schema.to_json()["fields"]]
    )
    # Handles Twitter authetification and the connection to Twitter Streaming API
    stream = Stream(auth,  my_tweet_producer)
    tracklist = ['#conovirus', '#COVID-19']
    stream.filter(track=tracklist)
