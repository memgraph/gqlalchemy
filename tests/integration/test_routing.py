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

These tests need a running HA cluster whose coordinator is advertised through
``MEMGRAPH_HA_COORDINATOR_HOST`` / ``MEMGRAPH_HA_COORDINATOR_PORT`` (started in
CI by the "Run Memgraph HA Cluster" step, ``scripts/ha_cluster.sh``, or locally
by running that script). They are skipped otherwise.
"""

import os

import mgclient
import pytest

from gqlalchemy import Memgraph
from gqlalchemy.connection import MemgraphConnection

HA_HOST = os.environ.get("MEMGRAPH_HA_COORDINATOR_HOST")
HA_PORT = os.environ.get("MEMGRAPH_HA_COORDINATOR_PORT")

pytestmark = [
    pytest.mark.routing,
    pytest.mark.skipif(
        not (HA_HOST and HA_PORT),
        reason="requires a Memgraph HA cluster (set MEMGRAPH_HA_COORDINATOR_HOST/PORT)",
    ),
]


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


def test_write_connection_targets_main():
    connection = _routing_connection(mgclient.ACCESS_MODE_WRITE)
    assert _replication_role(connection) == "main"


def test_read_connection_targets_replica():
    connection = _routing_connection(mgclient.ACCESS_MODE_READ)
    assert _replication_role(connection) == "replica"


def test_default_access_mode_targets_main():
    # No access_mode given -> pymgclient defaults to writes (the main).
    connection = _routing_connection()
    assert _replication_role(connection) == "main"


def test_routed_write_is_readable_from_main():
    connection = _routing_connection(mgclient.ACCESS_MODE_WRITE)
    connection.execute("MERGE (n:RoutingTest {id: 1}) SET n.value = 'ok'")
    result = list(connection.execute_and_fetch("MATCH (n:RoutingTest {id: 1}) RETURN n.value AS value"))
    assert result[0]["value"] == "ok"


# The Memgraph vendor client (routing plumbed through new_connection).


def _routing_memgraph(access_mode=None):
    return Memgraph(host=HA_HOST, port=int(HA_PORT), routing=True, access_mode=access_mode)


def _vendor_role(db):
    row = list(db.execute_and_fetch("SHOW REPLICATION ROLE"))[0]
    return next(iter(row.values()))


def test_vendor_write_client_targets_main():
    assert _vendor_role(_routing_memgraph(mgclient.ACCESS_MODE_WRITE)) == "main"


def test_vendor_read_client_targets_replica():
    assert _vendor_role(_routing_memgraph(mgclient.ACCESS_MODE_READ)) == "replica"


def test_vendor_default_access_mode_targets_main():
    assert _vendor_role(_routing_memgraph()) == "main"
