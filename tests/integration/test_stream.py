# Copyright (c) 2016-2022 Memgraph Ltd. [https://memgraph.com]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from gqlalchemy import MemgraphKafkaStream, MemgraphPulsarStream, Memgraph
from gqlalchemy.exceptions import GQLAlchemyError


def stream_exists(stream: str, memgraph: Memgraph) -> bool:
    return stream in memgraph.get_streams()


def test_create_kafka_stream(memgraph):
    kafka_stream = MemgraphKafkaStream(name="test_stream", topics=["topic"], transform="kafka_stream.transform")

    with pytest.raises(GQLAlchemyError) as e_info:
        memgraph.create_stream(kafka_stream)
    assert "Local: Broker transport failure" in str(e_info.value.message)


def test_create_pulsar_stream(memgraph):
    pulsar_stream = MemgraphPulsarStream(name="test_stream", topics=["topic"], transform="pulsar_stream.transform")

    with pytest.raises(GQLAlchemyError) as e_info:
        memgraph.create_stream(pulsar_stream)
    assert "Pulsar consumer test_stream : ConnectError" in str(e_info.value.message)


def test_drop_pulsar_stream(memgraph):
    pulsar_stream = MemgraphPulsarStream(name="test_stream", topics=["topic"], transform="pulsar_stream.transform")

    with pytest.raises(GQLAlchemyError) as e_info:
        memgraph.create_stream(pulsar_stream)
    assert "Pulsar consumer test_stream : ConnectError" in str(e_info.value.message)


def test_create_kafka_stream_cypher():
    kafka_stream = MemgraphKafkaStream(name="test_stream", topics=["topic"], transform="kafka_stream.transform")
    query = "CREATE KAFKA STREAM test_stream TOPICS topic TRANSFORM kafka_stream.transform;"
    assert kafka_stream.to_cypher() == query


def test_create_pulsar_stream_cypher():
    pulsar_stream = MemgraphPulsarStream(name="test_stream", topics=["topic"], transform="pulsar_stream.transform")
    query = "CREATE PULSAR STREAM test_stream TOPICS topic TRANSFORM pulsar_stream.transform;"
    assert pulsar_stream.to_cypher() == query


def test_start_kafka_stream(memgraph):
    kafka_stream = MemgraphKafkaStream(name="test_stream", topics=["topic"], transform="kafka_stream.transform")

    with pytest.raises(GQLAlchemyError) as e_info:
        memgraph.start_stream(kafka_stream)
    assert "Couldn't find stream 'test_stream'" in str(e_info.value.message)


def test_start_pulsar_stream(memgraph):
    pulsar_stream = MemgraphPulsarStream(name="test_stream", topics=["topic"], transform="pulsar_stream.transform")

    with pytest.raises(GQLAlchemyError) as e_info:
        memgraph.start_stream(pulsar_stream)
    assert "Couldn't find stream 'test_stream'" in str(e_info.value.message)


def test_kafka_stream_extended_cypher():
    kafka_stream = MemgraphKafkaStream(
        name="test_stream",
        topics=["topic"],
        transform="kafka_stream.transform",
        consumer_group="my_group",
        batch_interval="9999",
        bootstrap_servers="localhost:9092",
    )
    query = "CREATE KAFKA STREAM test_stream TOPICS topic TRANSFORM kafka_stream.transform CONSUMER_GROUP my_group BATCH_INTERVAL 9999 BOOTSTRAP_SERVERS 'localhost:9092';"
    assert kafka_stream.to_cypher() == query


def test_kafka_stream_extended_cypher_list():
    kafka_stream = MemgraphKafkaStream(
        name="test_stream",
        topics=["topic"],
        transform="kafka_stream.transform",
        consumer_group="my_group",
        batch_interval="9999",
        bootstrap_servers=["localhost:9092", "localhost:9093", "localhost:9094"],
    )
    query = "CREATE KAFKA STREAM test_stream TOPICS topic TRANSFORM kafka_stream.transform CONSUMER_GROUP my_group BATCH_INTERVAL 9999 BOOTSTRAP_SERVERS 'localhost:9092', 'localhost:9093', 'localhost:9094';"
    assert kafka_stream.to_cypher() == query


def test_pulsar_stream_extended_cypher():
    pulsar_stream = MemgraphPulsarStream(
        name="test_stream",
        topics=["topic"],
        transform="pulsar_stream.transform",
        batch_interval="9999",
        batch_size="99",
        service_url="'127.0.0.1:6650'",
    )
    query = "CREATE PULSAR STREAM test_stream TOPICS topic TRANSFORM pulsar_stream.transform BATCH_INTERVAL 9999 BATCH_SIZE 99 SERVICE_URL '127.0.0.1:6650';"
    assert pulsar_stream.to_cypher() == query
