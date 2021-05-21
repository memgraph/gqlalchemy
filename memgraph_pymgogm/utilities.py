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
