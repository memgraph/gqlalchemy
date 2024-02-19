# How to manage database triggers

Because Memgraph supports database triggers on `CREATE`, `UPDATE` and `DELETE`
operations, GQLAlchemy also implements a simple interface for maintaining these
triggers. 

!!! info
    You can also use this feature with Neo4j:

    ```python
    db = Neo4j(host="localhost", port="7687", username="neo4j", password="test")
    ```


## 1. Create the trigger

To set up the trigger, first, create a `MemgraphTrigger` object with all the
required arguments:

- `name: str` ➡ The name of the trigger.
- `event_type: TriggerEventType` ➡ The type of event that will trigger the
  execution. The options are: `TriggerEventType.CREATE`,
  `TriggerEventType.UPDATE` and `TriggerEventType.DELETE`.
- `event_object: TriggerEventObject` ➡ The objects that are affected with the
  `event_type`. The options are: ``TriggerEventObject.ALL,
  `TriggerEventObject.NODE` and `TriggerEventObject.RELATIONSHIP`.
- `execution_phase: TriggerExecutionPhase` ➡ The phase when the trigger should
  be executed in regard to the transaction commit. The options are: `BEFORE` and
  `AFTER`.
- `statement: str` ➡ The Cypher query that should be executed when the trigger
  fires.

Now, let's create a trigger in GQLAlchemy:

```python
from gqlalchemy import Memgraph, MemgraphTrigger
from gqlalchemy.models import (
    TriggerEventType,
    TriggerEventObject,
    TriggerExecutionPhase,
)

db = Memgraph()

trigger = MemgraphTrigger(
    name="ratings_trigger",
    event_type=TriggerEventType.CREATE,
    event_object=TriggerEventObject.NODE,
    execution_phase=TriggerExecutionPhase.AFTER,
    statement="UNWIND createdVertices AS node SET node.created_at = LocalDateTime()",
)

db.create_trigger(trigger)
```

The trigger names `ratings_trigger` will be executed every time a node is
created in the database. After the transaction that created the node in question
finishes, the Cypher query `statement` will execute, and in this case, it will
set the property `created_at` of the newly created node to the current date and
time. 

## 2. Check the status of a trigger

You can return all of the triggers from the database with the `get_Triggers()`
method:

```python
triggers = db.get_triggers()
print(triggers)
```

## 3. Delete the trigger

You can use the `drop_trigger()` method to delete a trigger:

```python
db.drop_trigger(trigger)
```
