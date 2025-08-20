# Copyright (c) 2016-2025 Memgraph Ltd. [https://memgraph.com]
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

import datetime
import pytz
from zoneinfo import ZoneInfo

from gqlalchemy import Memgraph


def test_date(memgraph: Memgraph):
    query = "RETURN date('2024-04-21') as value"
    result = list(memgraph.execute_and_fetch(query))

    assert len(result) == 1
    value = result[0]["value"]
    assert isinstance(value, datetime.date)
    assert value == datetime.date(2024, 4, 21)


def test_localtime(memgraph: Memgraph):
    query = "RETURN localTime('14:15:16.123') as value"
    result = list(memgraph.execute_and_fetch(query))

    assert len(result) == 1
    value = result[0]["value"]
    assert isinstance(value, datetime.time)
    assert value == datetime.time(14, 15, 16, 123000)


def test_localdatetime(memgraph: Memgraph):
    query = "RETURN localDateTime('2024-04-21T14:15:16.123') as value"
    result = list(memgraph.execute_and_fetch(query))

    assert len(result) == 1
    value = result[0]["value"]
    assert isinstance(value, datetime.datetime)
    assert value == datetime.datetime(2024, 4, 21, 14, 15, 16, 123000)
    assert value.tzinfo is None


def test_duration(memgraph: Memgraph):
    query = "RETURN duration('P1DT5H16M12.5S') as value"
    result = list(memgraph.execute_and_fetch(query))

    assert len(result) == 1
    value = result[0]["value"]
    assert isinstance(value, datetime.timedelta)
    assert value == datetime.timedelta(days=1, hours=5, minutes=16, seconds=12, microseconds=500000)


def test_zoned_datetime_with_named_timezone(memgraph: Memgraph):
    query = "RETURN datetime('2024-04-21T14:15:16[America/Los_Angeles]') as value"
    result = list(memgraph.execute_and_fetch(query))

    assert len(result) == 1
    value = result[0]["value"]
    assert isinstance(value, datetime.datetime)
    assert value.tzinfo is not None
    assert isinstance(value.tzinfo, ZoneInfo)
    assert value.tzinfo.key == "America/Los_Angeles"
    assert value.replace(tzinfo=None) == datetime.datetime(2024, 4, 21, 14, 15, 16)


def test_zoned_datetime_with_offset_timezone(memgraph: Memgraph):
    query = "RETURN datetime('2024-04-21T14:15:16+02:00') as value"
    result = list(memgraph.execute_and_fetch(query))

    assert len(result) == 1
    value = result[0]["value"]
    assert isinstance(value, datetime.datetime)
    assert value.tzinfo is not None
    assert isinstance(value.tzinfo, datetime.timezone)
    assert value.tzinfo.utcoffset(None) == datetime.timedelta(hours=2)
    assert value.replace(tzinfo=None) == datetime.datetime(2024, 4, 21, 14, 15, 16)


def test_zoned_datetime_utc(memgraph: Memgraph):
    query = "RETURN datetime('2024-04-21T14:15:16Z') as value"
    result = list(memgraph.execute_and_fetch(query))

    assert len(result) == 1
    value = result[0]["value"]
    assert isinstance(value, datetime.datetime)
    assert value.tzinfo is not None
    assert isinstance(value.tzinfo, ZoneInfo)
    assert value.tzinfo.key == "Etc/UTC"
    assert value.replace(tzinfo=None) == datetime.datetime(2024, 4, 21, 14, 15, 16)


def test_zoned_datetime_with_pytz_timezone(memgraph: Memgraph):
    tz = pytz.timezone("America/New_York")
    dt = tz.localize(datetime.datetime(2024, 4, 21, 14, 15, 16))

    result = list(memgraph.execute_and_fetch("RETURN $dt as value", {"dt": dt}))
    assert len(result) == 1
    value = result[0]["value"]

    assert isinstance(value, datetime.datetime)
    assert value.tzinfo is not None
    assert isinstance(value.tzinfo, ZoneInfo)
    assert str(value.tzinfo) == "America/New_York"
    assert value.replace(tzinfo=None) == datetime.datetime(2024, 4, 21, 14, 15, 16)


def test_zoned_datetime_with_pytz_utc(memgraph: Memgraph):
    dt = pytz.utc.localize(datetime.datetime(2024, 4, 21, 14, 15, 16))

    result = list(memgraph.execute_and_fetch("RETURN $dt as value", {"dt": dt}))
    assert len(result) == 1
    value = result[0]["value"]

    assert isinstance(value, datetime.datetime)
    assert value.tzinfo is not None
    assert isinstance(value.tzinfo, ZoneInfo)
    assert str(value.tzinfo) == "Etc/UTC"
    assert value.replace(tzinfo=None) == datetime.datetime(2024, 4, 21, 14, 15, 16)


def test_zoned_datetime_with_zoneinfo(memgraph: Memgraph):
    tz = ZoneInfo("America/Toronto")
    dt = datetime.datetime(2024, 4, 21, 14, 15, 16, tzinfo=tz)

    result = list(memgraph.execute_and_fetch("RETURN $dt as value", {"dt": dt}))
    assert len(result) == 1
    value = result[0]["value"]

    assert isinstance(value, datetime.datetime)
    assert value.tzinfo is not None
    assert isinstance(value.tzinfo, ZoneInfo)
    assert str(value.tzinfo) == "America/Toronto"
    assert value.replace(tzinfo=None) == datetime.datetime(2024, 4, 21, 14, 15, 16)
