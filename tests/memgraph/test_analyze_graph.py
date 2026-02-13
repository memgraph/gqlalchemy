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

from unittest.mock import patch

from gqlalchemy.vendors.memgraph import Memgraph


def test_analyze_graph_all_labels():
    """Test analyze_graph without specifying labels."""
    memgraph = Memgraph()
    mock_result = [
        {
            "label": "Person",
            "property": "name",
            "num estimation nodes": 100,
            "num groups": 50,
            "avg group size": 2.0,
            "chi-squared value": 0.5,
            "avg degree": 3.0,
        }
    ]

    with patch.object(Memgraph, "execute_and_fetch", return_value=iter(mock_result)) as mock:
        result = memgraph.analyze_graph()

    mock.assert_called_with("ANALYZE GRAPH;")
    assert result == mock_result


def test_analyze_graph_specific_labels():
    """Test analyze_graph with specific labels."""
    memgraph = Memgraph()
    mock_result = []

    with patch.object(Memgraph, "execute_and_fetch", return_value=iter(mock_result)) as mock:
        result = memgraph.analyze_graph(labels=["Person", "Company"])

    mock.assert_called_with("ANALYZE GRAPH ON LABELS :Person, :Company;")
    assert result == mock_result


def test_analyze_graph_single_label():
    """Test analyze_graph with a single label."""
    memgraph = Memgraph()
    mock_result = []

    with patch.object(Memgraph, "execute_and_fetch", return_value=iter(mock_result)) as mock:
        result = memgraph.analyze_graph(labels=["Person"])

    mock.assert_called_with("ANALYZE GRAPH ON LABELS :Person;")
    assert result == mock_result


def test_delete_graph_statistics_all():
    """Test delete_graph_statistics for all labels."""
    memgraph = Memgraph()
    mock_result = [{"label": "Person", "property": "name"}]

    with patch.object(Memgraph, "execute_and_fetch", return_value=iter(mock_result)) as mock:
        result = memgraph.delete_graph_statistics()

    mock.assert_called_with("ANALYZE GRAPH DELETE STATISTICS;")
    assert result == mock_result


def test_delete_graph_statistics_specific_labels():
    """Test delete_graph_statistics for specific labels."""
    memgraph = Memgraph()
    mock_result = []

    with patch.object(Memgraph, "execute_and_fetch", return_value=iter(mock_result)) as mock:
        result = memgraph.delete_graph_statistics(labels=["Person", "Company"])

    mock.assert_called_with("ANALYZE GRAPH ON LABELS :Person, :Company DELETE STATISTICS;")
    assert result == mock_result
