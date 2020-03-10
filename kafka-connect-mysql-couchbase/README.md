curl -s -SL \
'https://search.maven.org/remotecontent?filepath=org/mongodb/kafka/mongo-kafka-connect/1.0.1/mongo-kafka-connect-1.0.1.jar' \
-o /tmp/quickstart/mongojars/mongo-kafka-connect-1.0.1.jar

```bash
docker run \
--net="kafka-connect-samples_default" \
--rm curlimages/curl:7.68.0 \
-s \
-H $CT \
-d "$(cat samples.employees.source.json)" \
-X POST http://connect:8083/connectors
```

```bash
docker run \
--net="kafka-connect-samples_default" \
--rm curlimages/curl:7.68.0 \
-s \
-H $CT \
-d "$(cat samples.employees.target.json)" \
-X POST http://connect:8083/connectors
```