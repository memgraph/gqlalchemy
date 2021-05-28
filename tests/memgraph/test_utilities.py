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
from gqlalchemy.utilities import to_cypher_labels, to_cypher_properties, to_cypher_value


@pytest.mark.parametrize(
    "value, cypher_value",
    [
        ("abc", "'abc'"),
        ("null", "null"),
        (123, "123"),
        (3.14, "3.14"),
        ([1, 2, 3], "[1, 2, 3]"),
        ({"k1": 123, "k2": {"subkey1": "abc"}}, "{k1: 123, k2: {subkey1: 'abc'}}"),
        (None, "null"),
        (True, "True"),
    ],
)
def test_to_cypher_value(value, cypher_value):
    actual_value = to_cypher_value(value)

    assert actual_value == cypher_value


def test_to_cypher_properties():
    properties = {
        "prop1": "abc",
        "prop2": 123.321,
        "prop3": {"k1": [1, 2, 3], "k2": {"subkey1": 1, "subkey2": [3, 2, 1]}},
    }
    expected_properties = "{prop1: 'abc', prop2: 123.321, prop3: {k1: [1, 2, 3], k2: {subkey1: 1, subkey2: [3, 2, 1]}}}"

    actual_properties = to_cypher_properties(properties)

    assert actual_properties == expected_properties


def test_to_cypher_labels_single_label():
    label = "Label"
    expected_cypher_label = ":Label"

    actual_cypher_label = to_cypher_labels(label)

    assert actual_cypher_label == expected_cypher_label


def test_to_cypher_labels_multiple_label():
    labels = ["Label1", "Label2"]
    expected_cypher_label = ":Label1:Label2"

    actual_cypher_label = to_cypher_labels(labels)

    assert actual_cypher_label == expected_cypher_label
