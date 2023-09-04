## Transporter Objects

```python
class Transporter(ABC)
```

#### export

```python
@abstractmethod
def export(query_results)
```

Abstract method that will be overriden by subclasses that will know which correct graph type to create.

**Raises**:

- `NotImplementedError` - The method must be override by a specific translator.

