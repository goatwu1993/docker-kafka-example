sudo curl -k -SL \
    \"http://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-8.0.19.tar.gz\" |
    sudo tar -xzf - -C \
        /tmp/quickstart/jars \
        --strip-components=1 \
        mysql-connector-java-8.0.19/mysql-connector-java-8.0.19.jar

docker exec -i quickstart-mysql mysql -u confluent -pconfluent <<<"""
CREATE DATABASE IF NOT EXISTS connect_test;
USE connect_test;

DROP TABLE IF EXISTS test;

CREATE TABLE IF NOT EXISTS test (
  id serial NOT NULL PRIMARY KEY,
  name varchar(100),
  email varchar(200),
  department varchar(200),
  modified timestamp default CURRENT_TIMESTAMP NOT NULL,
  INDEX \`modified_index\` (\`modified\`)
);

INSERT INTO test (name, email, department) VALUES ('alice', 'alice@abc.com', 'engineering');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
SELECT * FROM test;
exit;
"""

docker run --rm \
    --net="${CONNECT_NET}" \
    -e CONNECT_LOG4J_ROOT_LOGLEVEL=OFF \
    confluentinc/cp-schema-registry:5.4.0 \
    kafka-avro-console-consumer \
    --bootstrap-server broker:29092 \
    --topic quickstart-jdbc-test \
    --from-beginning \
    --max-messages 10
