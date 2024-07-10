---
sidebar_label: transporter
title: gqlalchemy.transformations.export.transporter
---

## Transporter Objects

```python
class Transporter(ABC)
```

#### export

```python
@abstractmethod
def export(query_results)
```

Abstract method that will be overridden by subclasses that will know which correct graph type to create.

**Raises**:

- `NotImplementedError` - The method must be override by a specific translator.

