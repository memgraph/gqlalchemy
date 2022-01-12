# Copyright (c) 2016-2021 Memgraph Ltd. [https://memgraph.com]
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
from gqlalchemy import MemgraphKafkaStream, MemgraphPulsarStream


def stream_exists(streams, stream_name):
    return any(map(lambda s: s["name"] == stream_name, streams))


def test_create_kafka_stream(memgraph):
    kafka_stream = MemgraphKafkaStream(name="test_stream", topics=["topic"], transform="kafka_stream.transform")

    with pytest.raises(Exception) as e_info:
        memgraph.create_stream(kafka_stream)
    assert "Local: Broker transport failure" in str(e_info.value)


def test_drop_kafka_stream(memgraph):
    kafka_stream = MemgraphKafkaStream(name="test_stream", topics=["topic"], transform="kafka_stream.transform")

    with pytest.raises(Exception) as e_info:
        memgraph.create_stream(kafka_stream)
    assert "Local: Broker transport failure" in str(e_info.value)


def test_create_pulsar_stream(memgraph):
    pulsar_stream = MemgraphPulsarStream(name="test_stream", topics=["topic"], transform="pulsar_stream.transform")

    with pytest.raises(Exception) as e_info:
        memgraph.create_stream(pulsar_stream)
    assert "Pulsar consumer test_stream : ConnectError" in str(e_info.value)


def test_drop_pulsar_stream(memgraph):
    pulsar_stream = MemgraphPulsarStream(name="test_stream", topics=["topic"], transform="pulsar_stream.transform")

    with pytest.raises(Exception) as e_info:
        memgraph.create_stream(pulsar_stream)
    assert "Pulsar consumer test_stream : ConnectError" in str(e_info.value)


def test_kafka_stream_cypher():
    kafka_stream = MemgraphKafkaStream(name="test_stream", topics=["topic"], transform="kafka_stream.transform")
    query = "CREATE KAFKA STREAM test_stream TOPICS topic TRANSFORM kafka_stream.transform "
    assert kafka_stream.to_cypher() == query


def test_pulsar_stream_cypher():
    pulsar_stream = MemgraphKafkaStream(name="test_stream", topics=["topic"], transform="pulsar_stream.transform")
    query = "CREATE KAFKA STREAM test_stream TOPICS topic TRANSFORM pulsar_stream.transform "
    assert pulsar_stream.to_cypher() == query
