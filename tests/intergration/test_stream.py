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

from gqlalchemy import MemgraphKafkaStream, MemgraphPulsarStream


def test_create_kafka_stream(memgraph):
    kafka_stream = MemgraphKafkaStream(name="stream1", topics=["topic"], transform="kafka_stream.transform")

    memgraph.drop_stream(kafka_stream)
    memgraph.create_stream(kafka_stream)

    assert any(map(lambda s: s["name"] == "stream1", memgraph.get_streams()))
