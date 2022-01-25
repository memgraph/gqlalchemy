---
sidebar_label: connection
title: gqlalchemy.connection
---

## Connection Objects

```python
class Connection(ABC)
```

#### execute

```python
@abstractmethod
def execute(query: str) -> None
```

Executes Cypher query without returning any results.

#### execute\_and\_fetch

```python
@abstractmethod
def execute_and_fetch(query: str) -> Iterator[Dict[str, Any]]
```

Executes Cypher query and returns iterator of results.

#### is\_active

```python
@abstractmethod
def is_active() -> bool
```

Returns True if connection is active and can be used

#### create

```python
@staticmethod
def create(**kwargs) -> "Connection"
```

Creates an instance of a connection.

## MemgraphConnection Objects

```python
class MemgraphConnection(Connection)
```

#### execute

```python
def execute(query: str) -> None
```

Executes Cypher query without returning any results.

#### execute\_and\_fetch

```python
def execute_and_fetch(query: str) -> Iterator[Dict[str, Any]]
```

Executes Cypher query and returns iterator of results.

#### is\_active

```python
def is_active() -> bool
```

Returns True if connection is active and can be used

