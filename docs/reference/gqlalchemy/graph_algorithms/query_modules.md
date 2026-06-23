---
sidebar_label: query_modules
title: gqlalchemy.graph_algorithms.query_modules
---

## QueryModule Objects

```python
class QueryModule()
```

Class representing a single MAGE query module.

#### set\_argument\_values

```python
def set_argument_values(**kwargs) -> None
```

Set values for QueryModule arguments so the module can be called.

Kwargs:
Named arguments in self.arguments.

**Raises**:

- `KeyError` - Passed an argument not in the self.arguments list.

#### get\_arguments\_for\_call

```python
def get_arguments_for_call() -> str
```

return inputs in form "value1, value2, ..." for QueryBuilder call()
method.

**Raises**:

- `KeyError` - Cannot get all values of arguments because one or more is
  not set.

#### parse\_query\_module\_signature

```python
def parse_query_module_signature(
        signature: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]
```

Query Modules signatures received from Memgraph are parsed into a
list of dictionaries.

One list is for arguments and another for returns.
For instance, if a query module signature is:
dummy_module.dummy(lst :: LIST OF STRING, num = 3 :: NUMBER) :: (ret :: STRING)
the method should return a list of arguments:
[{"name": "lst", "type": "LIST OF STRING"}, {"name": "num", "type": "NUMBER", "default": 3}]
and a list of returns:
[{"name": "ret", "type": "STRING"}]

Dictionary consists of fields: "name" - argument name, "type" - data
type of argument and "default" where default argument value is given

**Arguments**:

- `signature` - module signature as returned by Cypher CALL operation

#### parse\_field

```python
def parse_field(
        vars_field: str,
        name_type_delimiter: str = NAME_TYPE_DELIMITER,
        default_value_delimiter: str = EQUALS_DELIMITER
) -> List[Dict[str, str]]
```

Parse a field of arguments or returns from Query Module signature.

**Arguments**:

- `vars_field` - signature field inside parenthesis

