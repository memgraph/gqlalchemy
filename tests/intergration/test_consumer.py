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
from gqlalchemy import KafkaConsumer, PulsarConsumer
import json

check = False


def test_kafka_consumer_init():
    kafka_consumer = KafkaConsumer("topic", bootstrap_servers="54.217.170.100:9093")

    assert kafka_consumer.consumer.config["bootstrap_servers"] == "54.217.170.100:9093"
    assert "topic" in kafka_consumer.consumer._client._topics


def test_pulsar_consumer_init():
    pulsar_consumer = PulsarConsumer(service_url="pulsar://54.217.170.100:6650")
    pulsar_consumer.subscribe("ratings", "test-subscription")

    assert "persistent://public/default/ratings" == pulsar_consumer.consumer.topic()


def print_consumed_kakfa_message(message):
    message = json.loads(message.value.decode("utf8"))
    if message:
        global check
        check = True
    return False


def print_consumed_pulsar_message(message):
    message = json.loads(message.data().decode("utf8"))
    if message:
        global check
        check = True
    return False


def test_kafka_consumer_consume_with_function():
    kafka_consumer = KafkaConsumer("ratings", bootstrap_servers="54.217.170.100:9093")
    kafka_consumer.consume_with_function(print_consumed_kakfa_message, 1)


def test_pulsar_consumer_consume_with_function():
    pulsar_consumer = PulsarConsumer(service_url="pulsar://54.217.170.100:6650")
    pulsar_consumer.subscribe("ratings", "test-subscription")
    pulsar_consumer.consume_with_function(print_consumed_pulsar_message, 1)
