# Copyright (c) 2016-2021 Memgraph Ltd. [https://memgraph.com]
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

from unittest.mock import patch

import pytest
from gqlalchemy import InvalidMatchChainException, Match, NoVariablesMatchedException
from gqlalchemy.memgraph import Memgraph


def test_invalid_match_chain_throws_exception():
    with pytest.raises(InvalidMatchChainException):
        Match().node(":Label", "n").node(":Label", "m")


def test_no_variables_matched_throws_exception():
    with pytest.raises(NoVariablesMatchedException):
        Match().node(":Label").execute()


class TestMatch:
    def test_simple_match(self):
        query_builder = Match().node("L1", variable="n").to("TO").node("L2")
        expected_query = "MATCH (n:L1)-[:TO]->(:L2) RETURN *"

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_simple_match_with_variables(self):
        query_builder = Match().node("L1", variable="n").to("TO", variable="e").node("L2", variable="m")
        expected_query = "MATCH (n:L1)-[e:TO]->(m:L2) RETURN *"

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_simple_with_multiple_labels(self):
        query_builder = Match().node(["L1", "L2", "L3"], variable="n").to("TO").node("L2", variable="m")
        expected_query = "MATCH (n:L1:L2:L3)-[:TO]->(m:L2) RETURN *"

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_multiple_matches(self):
        query_builder = (
            Match()
            .node("L1", variable="n")
            .to("TO")
            .node("L2", variable="m")
            .match(True)
            .node(variable="n")
            .to("TO")
            .node("L3")
        )
        expected_query = "MATCH (n:L1)-[:TO]->(m:L2) OPTIONAL MATCH (n)-[:TO]->(:L3) RETURN *"

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_where(self):
        query_builder = (
            Match()
            .node("L1", variable="n")
            .to("TO")
            .node("L2", variable="m")
            .where("n.name", "=", "best_name")
            .or_where("m.id", "<", 4)
        )
        expected_query = "MATCH (n:L1)-[:TO]->(m:L2) WHERE n.name = 'best_name' OR m.id < 4  RETURN *"

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)

    def test_get_single(self):
        query_builder = Match().node("L1", variable="n").to("TO").node("L2", variable="m")
        expected_query = "MATCH (n:L1)-[:TO]->(m:L2) RETURN n"

        with patch.object(Memgraph, "execute_and_fetch", return_value=iter([{"n": None}])) as mock:
            query_builder.get_single(retrieve="n")

        mock.assert_called_with(expected_query)

    def test_from(self):
        query_builder = Match().node("L1", variable="n").from_("TO", variable="e").node("L2", variable="m")
        expected_query = "MATCH (n:L1)<-[e:TO]-(m:L2) RETURN *"

        with patch.object(Memgraph, "execute_and_fetch", return_value=None) as mock:
            query_builder.execute()

        mock.assert_called_with(expected_query)
