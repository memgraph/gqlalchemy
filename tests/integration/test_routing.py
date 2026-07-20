# Copyright (c) 2016-2026 Memgraph Ltd. [https://memgraph.com]
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

"""Client-side routing against a Memgraph high-availability cluster.

Most of these tests need a running HA cluster whose coordinator is advertised
through ``MEMGRAPH_HA_COORDINATOR_HOST`` / ``MEMGRAPH_HA_COORDINATOR_PORT``
(started in CI by the "Run Memgraph HA Cluster" step, ``scripts/ha_cluster.sh``,
or locally by running that script); they carry ``@requires_cluster`` and are
skipped otherwise. The pure API-contract tests have no such requirement.
"""

import os

import mgclient
import pytest

from gqlalchemy import Memgraph, Node, GQLAlchemyError, GQLAlchemyTransientError
from gqlalchemy.connection import MemgraphConnection

HA_HOST = os.environ.get("MEMGRAPH_HA_COORDINATOR_HOST")
HA_PORT = os.environ.get("MEMGRAPH_HA_COORDINATOR_PORT")

pytestmark = pytest.mark.routing

requires_cluster = pytest.mark.skipif(
    not (HA_HOST and HA_PORT),
    reason="requires a Memgraph HA cluster (set MEMGRAPH_HA_COORDINATOR_HOST/PORT)",
)


def _routing_memgraph(access_mode=None, **kwargs):
    return Memgraph(host=HA_HOST, port=int(HA_PORT), routing=True, access_mode=access_mode, **kwargs)


# ---------------------------------------------------------------------------
# One-shot routed connection (Tier A): connect() picks the instance.
# ---------------------------------------------------------------------------


def _routing_connection(access_mode=None):
    """A routed ``MemgraphConnection`` against the cluster coordinator."""
    return MemgraphConnection(
        host=HA_HOST,
        port=int(HA_PORT),
        username="",
        password="",
        encrypted=False,
        routing=True,
        access_mode=access_mode,
    )


def _replication_role(connection):
    """Return 'main' or 'replica' for the instance a connection is bound to."""
    row = list(connection.execute_and_fetch("SHOW REPLICATION ROLE"))[0]
    return next(iter(row.values()))


@requires_cluster
def test_write_connection_targets_main():
    assert _replication_role(_routing_connection(mgclient.ACCESS_MODE_WRITE)) == "main"


@requires_cluster
def test_read_connection_targets_replica():
    assert _replication_role(_routing_connection(mgclient.ACCESS_MODE_READ)) == "replica"


@requires_cluster
def test_default_access_mode_targets_main():
    # No access_mode given -> pymgclient defaults to writes (the main).
    assert _replication_role(_routing_connection()) == "main"


@requires_cluster
def test_routed_write_is_readable_from_main():
    connection = _routing_connection(mgclient.ACCESS_MODE_WRITE)
    connection.execute("MERGE (n:RoutingTest {id: 1}) SET n.value = 'ok'")
    result = list(connection.execute_and_fetch("MATCH (n:RoutingTest {id: 1}) RETURN n.value AS value"))
    assert result[0]["value"] == "ok"


# ---------------------------------------------------------------------------
# The Memgraph vendor client with routing (Tier A plumbing).
# ---------------------------------------------------------------------------


def _vendor_role(db):
    row = list(db.execute_and_fetch("SHOW REPLICATION ROLE"))[0]
    return next(iter(row.values()))


@requires_cluster
def test_vendor_write_client_targets_main():
    assert _vendor_role(_routing_memgraph(mgclient.ACCESS_MODE_WRITE)) == "main"


@requires_cluster
def test_vendor_read_client_targets_replica():
    assert _vendor_role(_routing_memgraph(mgclient.ACCESS_MODE_READ)) == "replica"


@requires_cluster
def test_vendor_default_access_mode_targets_main():
    assert _vendor_role(_routing_memgraph()) == "main"


# ---------------------------------------------------------------------------
# Managed transactions via the long-lived Router (Tier C).
#
# execute_write / execute_read take a callable work(tx); tx exposes the usual
# execute / execute_and_fetch, and execute_and_fetch yields gqlalchemy-converted
# rows. The work may run more than once on retry, so it must be idempotent.
# ---------------------------------------------------------------------------


@requires_cluster
def test_execute_write_commits_and_is_readable():
    db = _routing_memgraph()

    def work(tx):
        tx.execute("MERGE (n:RoutingTest {id: 2}) SET n.value = 'managed'")
        return list(tx.execute_and_fetch("MATCH (n:RoutingTest {id: 2}) RETURN n.value AS value"))

    result = db.execute_write(work)
    assert result[0]["value"] == "managed"


@requires_cluster
def test_execute_write_returns_work_result():
    db = _routing_memgraph()
    assert db.execute_write(lambda tx: 42) == 42


@requires_cluster
def test_execute_read_returns_work_result():
    db = _routing_memgraph()
    result = db.execute_read(lambda tx: list(tx.execute_and_fetch("RETURN 1 AS one"))[0]["one"])
    assert result == 1


@requires_cluster
def test_execute_read_converts_graph_values():
    # Managed transactions return gqlalchemy models, like execute_and_fetch does.
    db = _routing_memgraph()
    db.execute_write(lambda tx: tx.execute("MERGE (:RoutingTest {id: 4})"))
    # Read the node back on the main (execute_write) to avoid replica lag.
    node = db.execute_write(lambda tx: list(tx.execute_and_fetch("MATCH (n:RoutingTest {id: 4}) RETURN n"))[0]["n"])
    assert isinstance(node, Node)


@requires_cluster
def test_execute_read_fails_over_across_replicas():
    # Make the first replica the router tries unreachable; the managed read must
    # refresh routing and succeed against another replica.
    killed = []

    def resolver(address):
        if not killed:
            killed.append(address)
        return ["127.0.0.1:1"] if address == killed[0] else [address]

    db = _routing_memgraph(mgclient.ACCESS_MODE_READ, resolver=resolver)
    result = db.execute_read(lambda tx: list(tx.execute_and_fetch("RETURN 1 AS one"))[0]["one"])
    assert result == 1


@requires_cluster
def test_execute_write_exhausts_retries_raises_transient():
    # Nothing is reachable, so the managed write exhausts its retry budget and
    # surfaces the transient classification.
    db = _routing_memgraph(
        resolver=lambda address: ["127.0.0.1:1"],
        max_retries=1,
        retry_backoff=0.01,
        retry_backoff_cap=0.02,
    )
    with pytest.raises(GQLAlchemyTransientError):
        db.execute_write(lambda tx: tx.execute("MERGE (:RoutingTest {id: 5})"))


@requires_cluster
def test_get_routing_table():
    table = _routing_memgraph().get_routing_table()
    assert {"ttl", "write", "read", "route"}.issubset(table.keys())
    assert table["write"]  # at least one main is advertised


def test_managed_transactions_require_routing():
    # No cluster needed: without routing there is no Router to manage them.
    db = Memgraph()
    with pytest.raises(GQLAlchemyError):
        db.execute_write(lambda tx: None)
    with pytest.raises(GQLAlchemyError):
        db.execute_read(lambda tx: None)
