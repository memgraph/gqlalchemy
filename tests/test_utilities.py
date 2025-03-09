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

import datetime
import math
import numpy as np
import pytest
import pytz

from gqlalchemy.utilities import (
    NanException,
    NanValuesHandle,
    NetworkXCypherConfig,
    to_cypher_labels,
    to_cypher_properties,
    to_cypher_value,
)


@pytest.mark.parametrize(
    "value, cypher_value",
    [
        ("abc", '"abc"'),
        ("null", "null"),
        ("possessive's", '"possessive\'s"'),
        ("Newline\ncharacter", '"Newline\\ncharacter"'),
        ("Single quote's\nwith a newline", '"Single quote\'s\\nwith a newline"'),
        (123, "123"),
        (3.14, "3.14"),
        ([1, 2, 3], "[1, 2, 3]"),
        ({"k1": 123, "k2": {"subkey1": "abc"}}, '{k1: 123, k2: {subkey1: "abc"}}'),
        (None, "null"),
        (True, "True"),
        (np.array([1, 2, 3]), "[1, 2, 3]"),
        (np.array([1.23, 2.34, 3.45]), "[1.23, 2.34, 3.45]"),
        (np.array(["1", "2", "3"]), '["1", "2", "3"]'),
        (np.array([[1, 2], [3, 4], [4, 5]]), "[[1, 2], [3, 4], [4, 5]]"),
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
    expected_properties = '{prop1: "abc", prop2: 123.321, prop3: {k1: [1, 2, 3], k2: {subkey1: 1, subkey2: [3, 2, 1]}}}'

    actual_properties = to_cypher_properties(properties)

    assert actual_properties == expected_properties


def test_to_cypher_datetime():
    date = datetime.date(1970, 1, 19)
    localtime = datetime.time(12, 12, 12)
    localdatetime = datetime.datetime(1999, 12, 12, 12, 12, 12)
    duration = datetime.timedelta(days=1, hours=5, minutes=16, seconds=12)
    zoned_dt_naive = datetime.datetime(2024, 4, 21, 14, 15, 0)
    zoned_dt = pytz.timezone("America/Los_Angeles").localize(zoned_dt_naive)
    zoned_dt_utc = datetime.datetime(2021, 4, 21, 14, 15, tzinfo=pytz.UTC)

    assert to_cypher_value(date) == "date('1970-01-19')"
    assert to_cypher_value(localtime) == "localTime('12:12:12')"
    assert to_cypher_value(localdatetime) == "localDateTime('1999-12-12T12:12:12')"
    assert to_cypher_value(duration) == "duration('P1DT5H16M12.0S')"
    assert to_cypher_value(zoned_dt) == "datetime('2024-04-21T14:15:00-07:00[America/Los_Angeles]')"
    assert to_cypher_value(zoned_dt_utc) == "datetime('2021-04-21T14:15:00Z')"


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


def test_nan_value_default_config_throw_exception():
    config = NetworkXCypherConfig()
    properties = {"prop1": math.nan}

    with pytest.raises(NanException):
        to_cypher_properties(properties, config)


def test_nan_value_no_config_throw_exception():
    properties = {"prop1": math.nan}

    with pytest.raises(NanException):
        to_cypher_properties(properties)


def test_nan_value_remove_handler_yields_null():
    config = NetworkXCypherConfig(nan_handler=NanValuesHandle.REMOVE_PROPERTY)

    properties = {"prop1": math.nan}
    expected_properties = "{prop1: null}"

    actual_properties = to_cypher_properties(properties, config)
    assert actual_properties == expected_properties
