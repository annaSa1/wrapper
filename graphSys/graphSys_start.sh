#!/bin/bash

# Start geth server

# TODO add geth user
screen
# screen -x
/opt/go-ethereum/build/bin/geth --datadir /local_datastore/ethereum --syncmode fast --rpc


# Start gremlin-server
su janusgraph
screen
# screen -x
cd
export JAVA_HOME=/usr/java/jdk1.8.0_162
bin/gremlin-server.sh ./conf/gremlin-server/http-gremlin-server.yaml 2>&1 > /var/log/janusgraph/gremlin-server.session.log &
