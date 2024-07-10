---
sidebar_label: exceptions
title: gqlalchemy.exceptions
---

#### connection\_handler

```python
def connection_handler(func,
                       delay: float = 0.01,
                       timeout: float = 5.0,
                       backoff: int = 2)
```

Wrapper for a wait on the connection.

**Arguments**:

- `func` - A function that tries to create the connection
- `delay` - A float that defines how long to wait between retries.
- `timeout` - A float that defines how long to wait for the port.
- `backoff` - An integer used for multiplying the delay.
  

**Raises**:

- `GQLAlchemyWaitForConnectionError` - Raises an error
  after the timeout period has passed.

