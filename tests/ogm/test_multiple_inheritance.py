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
from typing import Optional

from gqlalchemy import Node, Field


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_multiple_inheritance(database):
    class User(Node):
        name: Optional[str] = Field(unique=True, db=database)

    class Streamer(User):
        id: Optional[str] = Field(unique=True, db=database)
        name: Optional[str] = Field(unique=True, db=database)

    user = User(name="Ivan").save(database)
    streamer = Streamer(id=7, name="Pero").save(database)
    assert User.labels == {"User"}
    assert Streamer.labels == {"Streamer", "User"}
    assert user._labels == {"User"}
    assert streamer._labels == {"Streamer", "User"}
