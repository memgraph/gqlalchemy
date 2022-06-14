# Copyright (c) 2016-2022 Memgraph Ltd. [https://memgraph.com]
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

from gqlalchemy import Node, Field


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_load_node(database):
    class User(Node):
        name: str = Field(unique=True, db=database)

    class Streamer(User):
        name: str = Field(unique=True, db=database)
        id: str = Field(index=True, db=database)
        followers: int = Field()
        totalViewCount: int = Field()

    streamer = Streamer(name="Mislav", id="7", followers=777, totalViewCount=7777).save(database)
    loaded_streamer = database.load_node(streamer)
    assert loaded_streamer.name == "Mislav"
    assert loaded_streamer.id == "7"
    assert loaded_streamer.followers == 777
    assert loaded_streamer.totalViewCount == 7777
    assert loaded_streamer._labels == {"Streamer", "User"}
