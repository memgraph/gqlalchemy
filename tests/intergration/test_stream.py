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

from gqlalchemy import MemgraphKafkaStream


def stream_exists(streams, stream_name):
    return map(lambda s: s["name"] == stream_name, streams)


def test_create_kafka_stream(memgraph):
    kafka_stream = MemgraphKafkaStream(name="stream1", topics=["topic"], transform="kafka_stream.transform")

    # NOTE: Memgraph doesn't have DROP STREAMS; query.
    if stream_exists(memgraph.get_streams(), kafka_stream.name):
        memgraph.drop_stream(kafka_stream)

    memgraph.create_stream(kafka_stream)
    assert stream_exists(memgraph.get_streams(), kafka_stream.name)


# TODO(gitbuda): Add all streams tests.
