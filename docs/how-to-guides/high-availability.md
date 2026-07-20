# How to connect to a high-availability cluster

Through this guide, you will learn how to use GQLAlchemy to connect to a
[Memgraph high-availability (HA) cluster](https://memgraph.com/docs/clustering/high-availability)
with client-side routing: you point GQLAlchemy at a *coordinator* and it routes
each query to the right data instance — writes to the main, reads to a replica.

- [How to connect to a high-availability cluster](#how-to-connect-to-a-high-availability-cluster)
  - [Route a client through a coordinator](#route-a-client-through-a-coordinator)
  - [Choose an access mode](#choose-an-access-mode)
  - [Run managed transactions](#run-managed-transactions)
  - [Handle transient errors and tune retries](#handle-transient-errors-and-tune-retries)
  - [Resolve advertised addresses](#resolve-advertised-addresses)
  - [Inspect the routing table](#inspect-the-routing-table)

>If you have any more questions, join our community and ping us on [Discord](https://discord.gg/memgraph).

!!! info
    High availability is a [Memgraph Enterprise](https://memgraph.com/docs/database-management/enabling-memgraph-enterprise)
    feature, so you need a running HA cluster (coordinators and data instances)
    to use the features below. Client-side routing requires `pymgclient>=1.6.0`,
    which GQLAlchemy depends on. If you're unsure how to run an HA cluster, check
    out the Memgraph [high-availability documentation](https://memgraph.com/docs/clustering/high-availability).

## Route a client through a coordinator

Create a [`Memgraph`](../reference/gqlalchemy/vendors/memgraph.md) client with
`routing=True` and point its `host`/`port` at a cluster **coordinator** rather
than a specific data instance. GQLAlchemy fetches the cluster topology from the
coordinator and routes queries accordingly:

```python
from gqlalchemy import Memgraph

db = Memgraph(host="coordinator-1", port=7687, routing=True)

# Routed to the main.
db.execute("MERGE (:Person {name: 'Ada'})")

# Also routed to the main (the default access mode serves both reads and writes).
for result in db.execute_and_fetch("MATCH (n:Person) RETURN n.name AS name"):
    print(result["name"])
```

With `routing=False` (the default) GQLAlchemy connects directly to the given
`host`/`port`, exactly as before.

## Choose an access mode

`access_mode` selects which instance a routed client connects to: `"WRITE"` (the
default) targets the main, `"READ"` targets a replica. You can pass the string
or the `mgclient` constant:

```python
from gqlalchemy import Memgraph

# A read-only client, routed to a replica.
reader = Memgraph(host="coordinator-1", port=7687, routing=True, access_mode="READ")
for result in reader.execute_and_fetch("MATCH (n:Person) RETURN count(n) AS count"):
    print(result["count"])
```

```python
import mgclient
from gqlalchemy import Memgraph

writer = Memgraph(
    host="coordinator-1",
    port=7687,
    routing=True,
    access_mode=mgclient.ACCESS_MODE_WRITE,
)
```

!!! info
    A routed client opens its connection to whichever instance was current when
    it connected. To keep working through a failover — where the main changes —
    use the managed transactions described below, which re-route and retry
    automatically.

## Run managed transactions

For failover-safe operations, use [`execute_write()`](../reference/gqlalchemy/vendors/memgraph.md#execute_write)
and [`execute_read()`](../reference/gqlalchemy/vendors/memgraph.md#execute_read).
Each takes a `work` callable that receives a transaction object exposing the
usual `execute` / `execute_and_fetch`; the transaction is routed (writes to the
main, reads to a replica), committed for you, and **retried automatically** if
the cluster is briefly in flux (for example while a new main is being elected).
Whatever `work` returns is returned to you:

```python
from gqlalchemy import Memgraph

db = Memgraph(host="coordinator-1", port=7687, routing=True)

def add_person(tx):
    tx.execute("MERGE (:Person {name: $name})", {"name": "Ada"})
    rows = list(tx.execute_and_fetch("MATCH (n:Person) RETURN count(n) AS count"))
    return rows[0]["count"]

count = db.execute_write(add_person)

def count_people(tx):
    rows = list(tx.execute_and_fetch("MATCH (:Person) RETURN count(*) AS count"))
    return rows[0]["count"]

total = db.execute_read(count_people)
```

!!! warning
    Because a managed transaction may run **more than once** on retry, make the
    `work` idempotent — use `MERGE` rather than `CREATE` so a re-run cannot
    duplicate a write. Materialize any results you need (e.g. wrap
    `execute_and_fetch` in `list(...)`) before returning them, since the
    transaction is closed once `work` returns.

## Handle transient errors and tune retries

If a managed transaction cannot complete even after refreshing the routing table
and exhausting its retries, GQLAlchemy raises
[`GQLAlchemyTransientError`](../reference/gqlalchemy/exceptions.md) — a subclass
of `GQLAlchemyDatabaseError`, so existing error handling keeps working while
letting you single out retryable failures:

```python
from gqlalchemy import Memgraph, GQLAlchemyTransientError

db = Memgraph(host="coordinator-1", port=7687, routing=True)

try:
    db.execute_write(add_person)
except GQLAlchemyTransientError:
    # The cluster did not settle within the retry budget; surface or re-queue.
    raise
```

The retry budget is configurable on the client. Backoff is capped exponential —
`retry_backoff`, `2 * retry_backoff`, … up to `retry_backoff_cap` seconds:

```python
db = Memgraph(
    host="coordinator-1",
    port=7687,
    routing=True,
    max_retries=8,
    retry_backoff=1.0,
    retry_backoff_cap=15.0,
)
```

## Resolve advertised addresses

If the addresses the cluster advertises are not directly reachable from the
client (for example in-cluster names reached from outside, or a port-forward),
pass a `resolver` — a callable that maps an advertised `"host:port"` to a list
of reachable targets to try:

```python
from gqlalchemy import Memgraph

def resolver(advertised):
    mapping = {"memgraph-data-0.default.svc.cluster.local:7687": "127.0.0.1:7687"}
    return [mapping.get(advertised, advertised)]

db = Memgraph(host="127.0.0.1", port=7687, routing=True, resolver=resolver)
```

## Inspect the routing table

To see the topology the coordinator reports, use
[`get_routing_table()`](../reference/gqlalchemy/vendors/memgraph.md#get_routing_table).
It returns a dict with `ttl`, `write`, `read` and `route` entries:

```python
from gqlalchemy import Memgraph

db = Memgraph(host="coordinator-1", port=7687, routing=True)

table = db.get_routing_table()
print("main(s):", table["write"])
print("replica(s):", table["read"])
print("coordinator(s):", table["route"])
```

>Hopefully, this guide has taught you how to connect to a Memgraph
>high-availability cluster using GQLAlchemy. If you have any more questions, join
>our community and ping us on [Discord](https://discord.gg/memgraph).
