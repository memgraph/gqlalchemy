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

import json
from typing import Dict

import mgp
from kafka.producer import KafkaProducer


producers_by_name: Dict[str, KafkaProducer] = {}
topics_by_name: Dict[str, str] = {}


@mgp.read_proc
def create_push_stream(
    context: mgp.ProcCtx,
    stream_name: str,
    topic: str,
    config: mgp.Map,
) -> mgp.Record(created=bool):

    if not isinstance(stream_name, str):
        raise TypeError("Invalid type on first argument!")

    if not isinstance(topic, str):
        raise TypeError("Invalid type on second argument!")

    producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode("utf-8"), **config)

    producers_by_name[stream_name] = producer
    topics_by_name[stream_name] = topic

    return mgp.Record(created=True)


@mgp.read_proc
def show_streams(
    context: mgp.ProcCtx,
) -> mgp.Record(name=str, topic=str):
    records = []

    for k, v in topics_by_name.items():
        records.append(mgp.Record(name=k, topic=v))

    return records


@mgp.read_proc
def push(
    context: mgp.ProcCtx,
    stream_name: str,
    payload: mgp.Map,
) -> mgp.Record(message=mgp.Map):

    if not isinstance(stream_name, str):
        raise TypeError("Invalid type on first argument!")

    if not isinstance(payload, mgp.Map):
        raise TypeError("Invalid type on second argument!")

    if stream_name not in producers_by_name or stream_name not in topics_by_name:
        raise Exception(f"Stream {stream_name} is not present!")

    message = ""
    if isinstance(payload, dict):
        message = payload
    elif isinstance(payload, mgp.Vertex) or isinstance(payload, mgp.Edge):
        message = {x.name: x.value for x in payload.properties.items()}
    else:
        raise Exception("Can't have message type other than Map / Vertex / Edge")

    producer, topic = producers_by_name[stream_name], topics_by_name[stream_name]

    try:
        producer.send(topic, message)
    except Exception as e:
        raise Exception(f"Exception when sending message: {e}")

    return mgp.Record(message=message)
