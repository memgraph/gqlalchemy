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

from typing import Any, Dict, List, Optional, Union


def to_cypher_value(value: Any) -> str:
    """Converts value to a valid openCypher type"""
    value_type = type(value)

    if value_type == str and value.lower() == "null":
        return value

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


def to_cypher_properties(properties: Optional[Dict[str, Any]] = None) -> str:
    """Converts properties to a openCypher key-value properties"""
    if not properties:
        return ""

    properties_str = []
    for key, value in properties.items():
        value_str = to_cypher_value(value)
        properties_str.append(f"{key}: {value_str}")

    return "{{{}}}".format(", ".join(properties_str))


def to_cypher_labels(labels: Union[str, List[str], None]) -> str:
    """Converts labels to a openCypher label definition"""
    if labels:
        if isinstance(labels, str):
            return f":{labels}"
        return f":{':'.join(labels)}"
    return ""
