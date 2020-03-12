#!/bin/bash

echo "||||||||| Installing Employees database...||||||||||"
mysql -u confluent -pconfluent -t < /etc/start.sql
