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
from typing import List, Optional

from gqlalchemy import Field, Node, validator


@pytest.mark.parametrize("database", ["neo4j", "memgraph"], indirect=True)
def test_raise_value_error(database):
    class User(Node):
        name: str = Field(unique=True, db=database)
        age: int = Field()
        friends: Optional[List[str]] = Field()

        @validator("name", allow_reuse=True)
        def name_can_not_be_empty(cls, v):
            if v == "":
                raise ValueError("name can't be empty")

            return v

        @validator("age", allow_reuse=True)
        def age_must_be_greater_than_zero(cls, v):
            if v <= 0:
                raise ValueError("age must be greater than zero")

            return v

        @validator("friends", each_item=True, allow_reuse=True)
        def friends_must_be_(cls, v):
            if v == "":
                raise ValueError("name can't be empty")

            return v

    with pytest.raises(ValueError):
        User(name="", age=26).save(database)

    with pytest.raises(ValueError):
        User(name="Kate", age=0).save(database)

    with pytest.raises(ValueError):
        User(name="Kate", age=26, friends=["Ema", "Ana", ""]).save(database)
