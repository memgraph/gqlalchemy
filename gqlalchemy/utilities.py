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

import math

from enum import Enum
from typing import Any, Dict, List, Optional, Union


class GQLAlchemyWarning(Warning):
    pass


class NanValuesHandle(Enum):
    THROW_EXCEPTION = 1
    REMOVE_PROPERTY = 2


class NetworkXCypherConfig:
    def __init__(self, create_index: bool = False, nan_handler: NanValuesHandle = NanValuesHandle.THROW_EXCEPTION):
        self._create_index = create_index
        self._nan_handler = nan_handler

    @property
    def create_index(self) -> bool:
        return self._create_index

    @property
    def nan_handler(self) -> NanValuesHandle:
        return self._nan_handler


def to_cypher_value(value: Any, config: NetworkXCypherConfig = None) -> str:
    """Converts value to a valid openCypher type"""
    if config is None:
        config = NetworkXCypherConfig()

    value_type = type(value)

    if value_type == str and value.lower() == "null":
        return value

    if value_type == float and math.isnan(value):
        if config.nan_handler == NanValuesHandle.THROW_EXCEPTION:
            raise NanException("Nan values are not allowed!")

        return "null"

    if value_type in [int, float, bool]:
        return str(value)

    if value_type in [list, set, tuple]:
        return f"[{', '.join(map(to_cypher_value, value))}]"

    if value_type == dict:
        lines = ", ".join(f"{k}: {to_cypher_value(v)}" for k, v in value.items())
        return f"{{{lines}}}"

    if value is None:
        return "null"

    if value.lower() in ["true", "false"]:
        return value

    return f"'{value}'"


def to_cypher_properties(properties: Optional[Dict[str, Any]] = None, config=None) -> str:
    """Converts properties to a openCypher key-value properties"""
    if config is None:
        config = NetworkXCypherConfig()

    if not properties:
        return ""

    properties_str = []
    for key, value in properties.items():
        value_str = to_cypher_value(value, config)
        properties_str.append(f"{key}: {value_str}")

    return "{{{}}}".format(", ".join(properties_str))


def to_cypher_labels(labels: Union[str, List[str], None]) -> str:
    """Converts labels to a openCypher label definition"""
    if labels:
        if isinstance(labels, str):
            return f":{labels}"
        return f":{':'.join(labels)}"
    return ""


class NanException(Exception):
    pass
