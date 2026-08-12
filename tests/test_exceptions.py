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

import mgclient
import pytest

from gqlalchemy.exceptions import (
    GQLAlchemyDatabaseError,
    GQLAlchemyTransientError,
    database_error_handler,
)


def test_transient_error_is_a_database_error():
    # Backwards compatible: code catching GQLAlchemyDatabaseError still catches
    # the transient subclass.
    assert issubclass(GQLAlchemyTransientError, GQLAlchemyDatabaseError)


def test_transient_error_is_mapped_to_gqlalchemy_transient_error():
    @database_error_handler
    def boom():
        raise mgclient.TransientError("instance briefly unreachable during a failover")

    with pytest.raises(GQLAlchemyTransientError):
        boom()


def test_non_transient_database_error_is_not_transient():
    @database_error_handler
    def boom():
        raise mgclient.DatabaseError("syntax error")

    with pytest.raises(GQLAlchemyDatabaseError) as exc_info:
        boom()
    assert not isinstance(exc_info.value, GQLAlchemyTransientError)


def test_plain_exception_is_mapped_to_database_error():
    @database_error_handler
    def boom():
        raise ValueError("not a database error")

    with pytest.raises(GQLAlchemyDatabaseError) as exc_info:
        boom()
    assert not isinstance(exc_info.value, GQLAlchemyTransientError)
