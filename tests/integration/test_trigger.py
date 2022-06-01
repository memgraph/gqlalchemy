# Copyright (c) 2016-2022 Memgraph Ltd. [https://memgraph.com]
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

import pytest

from gqlalchemy import Memgraph, MemgraphTrigger
from gqlalchemy.models import TriggerEventObject, TriggerEventType, TriggerExecutionPhase


@pytest.fixture
def cleanup_trigger():
    memgraph = Memgraph()
    memgraph.drop_triggers()
    yield
    memgraph.drop_triggers()


@pytest.mark.usefixtures("cleanup_trigger")
def test_create_trigger_without_event_object(memgraph: Memgraph):
    trigger = MemgraphTrigger(
        name="test_trigger",
        event_type=TriggerEventType.CREATE,
        execution_phase=TriggerExecutionPhase.BEFORE,
        statement="CREATE (:Node)",
    )

    memgraph.create_trigger(trigger)
    assert any(map(lambda t: t.name == "test_trigger", memgraph.get_triggers()))


def test_drop_trigger(memgraph: Memgraph):
    trigger = MemgraphTrigger(
        name="test_trigger",
        event_type=TriggerEventType.CREATE,
        execution_phase=TriggerExecutionPhase.BEFORE,
        statement="CREATE (:Node)",
    )

    memgraph.create_trigger(trigger)
    memgraph.drop_trigger(trigger)
    assert len(memgraph.get_triggers()) == 0


def test_trigger_cypher():
    trigger = MemgraphTrigger(
        name="test_trigger",
        event_type=TriggerEventType.CREATE,
        execution_phase=TriggerExecutionPhase.BEFORE,
        statement="CREATE (:Node)",
    )
    query = "CREATE TRIGGER test_trigger ON CREATE BEFORE COMMIT EXECUTE CREATE (:Node);"
    assert trigger.to_cypher() == query


@pytest.mark.usefixtures("cleanup_trigger")
def test_create_trigger_with_event_object(memgraph: Memgraph):
    trigger = MemgraphTrigger(
        name="test_trigger",
        event_type=TriggerEventType.CREATE,
        event_object=TriggerEventObject.NODE,
        execution_phase=TriggerExecutionPhase.AFTER,
        statement="CREATE (:Node)",
    )

    memgraph.create_trigger(trigger)
    assert any(map(lambda t: t.name == "test_trigger", memgraph.get_triggers()))


def test_trigger_with_event_object_cypher(memgraph: Memgraph):
    trigger = MemgraphTrigger(
        name="test_trigger",
        event_type=TriggerEventType.CREATE,
        event_object=TriggerEventObject.NODE,
        execution_phase=TriggerExecutionPhase.AFTER,
        statement="CREATE (:Node)",
    )

    query = "CREATE TRIGGER test_trigger ON () CREATE AFTER COMMIT EXECUTE CREATE (:Node);"
    assert trigger.to_cypher() == query


@pytest.mark.usefixtures("cleanup_trigger")
def test_create_trigger_without_on(memgraph: Memgraph):
    trigger = MemgraphTrigger(
        name="test_trigger",
        execution_phase=TriggerExecutionPhase.BEFORE,
        statement="CREATE (n:Node)",
    )

    memgraph.create_trigger(trigger)
    assert any(map(lambda t: t.name == "test_trigger", memgraph.get_triggers()))


def test_trigger_without_on_cypher():
    trigger = MemgraphTrigger(
        name="test_trigger",
        execution_phase=TriggerExecutionPhase.BEFORE,
        statement="CREATE (:Node)",
    )

    query = "CREATE TRIGGER test_trigger BEFORE COMMIT EXECUTE CREATE (:Node);"
    assert trigger.to_cypher() == query
