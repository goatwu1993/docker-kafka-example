# Schema used by AvroProducer

key_schema_str = """
{
   "namespace": "my.test",
   "name": "value",
   "type": "record",
   "fields" : [
     {
       "name" : "name",
       "type" : "string"
     }
   ]
}
"""

value_schema_str = """
{
  "name": "MyClass",
  "type": "record",
  "namespace": "com.acme.avro",
  "fields": [
    {
      "name": "created_at",
      "type": "string"
    },
    {
      "name": "id",
      "type": "long"
    },
    {
      "name": "id_str",
      "type": "string"
    },
    {
      "name": "text",
      "type": "string"
    },
    {
      "name": "retweet_count",
      "type": "int"
    },
    {
      "name": "favorite_count",
      "type": "int"
    },
    {
      "name": "favorited",
      "type": "boolean"
    },
    {
      "name": "retweeted",
      "type": "boolean"
    },
    {
      "name": "lang",
      "type": "string"
    }
  ]
}
"""
