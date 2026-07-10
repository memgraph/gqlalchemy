#!/bin/bash

# Start (or stop) a local Memgraph high-availability cluster in Docker: three
# data instances and three coordinators. Used by CI and for running the
# client-side routing tests locally.
#
# High availability is a Memgraph Enterprise feature, so `start` requires:
#   MEMGRAPH_ENTERPRISE_LICENSE, MEMGRAPH_ORGANIZATION_NAME
#
# The containers use host networking, so every instance shares localhost and
# gets a distinct port. The ports sit above the ones the rest of the test
# suite uses (7687 for the standalone Memgraph, 7688 for Neo4j) so the cluster
# can run alongside them. The advertised addresses are 127.0.0.1:<port>, which
# are directly reachable from the test runner on the host, so no address
# resolver is needed.
#
# Usage:
#   scripts/ha_cluster.sh start   # start, register the topology, wait to converge
#   scripts/ha_cluster.sh stop    # stop and remove the containers
#
# On success `start` prints the coordinator to point clients at, e.g.:
#   MEMGRAPH_HA_COORDINATOR_HOST=127.0.0.1 MEMGRAPH_HA_COORDINATOR_PORT=7703

set -Eeuo pipefail

IMAGE="${MEMGRAPH_HA_IMAGE:-memgraph/memgraph}"

DATA_NAMES=(mg-data1 mg-data2 mg-data3)
COORD_NAMES=(mg-coord1 mg-coord2 mg-coord3)

# Per-instance ports, indexed 0..2. Bolt ports start at 7700 to clear 7687/7688.
DATA_BOLT=(7700 7701 7702)
COORD_BOLT=(7703 7704 7705)
DATA_MGMT=(13011 13012 13013)
COORD_MGMT=(13021 13022 13023)
COORD_CPORT=(12121 12122 12123)
DATA_REPL=(10001 10002 10003)

# Run mgconsole (bundled in the memgraph image) against the bootstrap
# coordinator, reading queries from stdin.
mgconsole() {
  docker exec -i mg-coord1 mgconsole --host localhost --port "${COORD_BOLT[0]}"
}

stop_cluster() {
  for name in "${DATA_NAMES[@]}" "${COORD_NAMES[@]}"; do
    docker stop "$name" >/dev/null 2>&1 || true
  done
}

start_cluster() {
  if [ -z "${MEMGRAPH_ENTERPRISE_LICENSE:-}" ] ||
     [ -z "${MEMGRAPH_ORGANIZATION_NAME:-}" ]; then
    echo "error: set MEMGRAPH_ENTERPRISE_LICENSE and MEMGRAPH_ORGANIZATION_NAME" \
         "(high availability is a Memgraph Enterprise feature)" >&2
    exit 1
  fi

  local lic=(-e "MEMGRAPH_ENTERPRISE_LICENSE=$MEMGRAPH_ENTERPRISE_LICENSE" \
             -e "MEMGRAPH_ORGANIZATION_NAME=$MEMGRAPH_ORGANIZATION_NAME")

  # Three data instances.
  local i
  for i in 0 1 2; do
    docker run -d --rm --name "${DATA_NAMES[$i]}" --network host "${lic[@]}" \
      "$IMAGE" --bolt-port="${DATA_BOLT[$i]}" \
      --management-port="${DATA_MGMT[$i]}" --telemetry-enabled=false
  done

  # Three coordinators for a Raft quorum. mg-coord1 is the bootstrap leader;
  # the others are added during registration below.
  for i in 0 1 2; do
    docker run -d --rm --name "${COORD_NAMES[$i]}" --network host "${lic[@]}" \
      "$IMAGE" --bolt-port="${COORD_BOLT[$i]}" --coordinator-id="$((i + 1))" \
      --coordinator-port="${COORD_CPORT[$i]}" \
      --coordinator-hostname=127.0.0.1 \
      --management-port="${COORD_MGMT[$i]}" --telemetry-enabled=false
  done

  # Fail early (with logs) if any container didn't come up, rather than as an
  # opaque connection error later.
  sleep 10
  for name in "${DATA_NAMES[@]}" "${COORD_NAMES[@]}"; do
    if [ "$(docker inspect -f '{{.State.Running}}' "$name" 2>/dev/null)" != "true" ]; then
      echo "error: Memgraph HA container $name is not running" >&2
      docker logs "$name" || true
      exit 1
    fi
  done

  # Register the topology on the bootstrap coordinator.
  {
    for i in 1 2; do
      printf 'ADD COORDINATOR %d WITH CONFIG {"bolt_server": "127.0.0.1:%s", "coordinator_server": "127.0.0.1:%s", "management_server": "127.0.0.1:%s"};\n' \
        "$((i + 1))" \
        "${COORD_BOLT[$i]}" "${COORD_CPORT[$i]}" "${COORD_MGMT[$i]}"
    done
    for i in 0 1 2; do
      printf 'REGISTER INSTANCE instance_%d WITH CONFIG {"bolt_server": "127.0.0.1:%s", "management_server": "127.0.0.1:%s", "replication_server": "127.0.0.1:%s"};\n' \
        "$((i + 1))" \
        "${DATA_BOLT[$i]}" "${DATA_MGMT[$i]}" "${DATA_REPL[$i]}"
    done
    printf 'SET INSTANCE instance_1 TO MAIN;\n'
  } | mgconsole

  # Wait for the cluster to converge: the coordinator must advertise a main
  # (WRITE) and at least one replica.
  local converged=false instances=""
  for _ in $(seq 1 60); do
    instances="$(echo 'SHOW INSTANCES;' | mgconsole 2>/dev/null || true)"
    if echo "$instances" | grep -qiw main &&
       echo "$instances" | grep -qiw replica; then
      converged=true
      break
    fi
    sleep 1
  done
  if [ "$converged" != "true" ]; then
    echo "error: HA cluster did not converge" >&2
    echo "$instances" >&2
    exit 1
  fi

  echo "HA cluster ready. Point clients at the coordinator:"
  echo "  MEMGRAPH_HA_COORDINATOR_HOST=127.0.0.1" \
       "MEMGRAPH_HA_COORDINATOR_PORT=${COORD_BOLT[0]}"
}

case "${1:-start}" in
  start) start_cluster ;;
  stop) stop_cluster ;;
  *)
    echo "usage: $0 [start|stop]" >&2
    exit 2
    ;;
esac
