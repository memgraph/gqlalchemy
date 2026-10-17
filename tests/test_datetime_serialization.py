from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
import pytz

from gqlalchemy import Node
from gqlalchemy.utilities import to_cypher_value


@pytest.mark.parametrize("serializer", [to_cypher_value, Node().escape_value], ids=["utility", "model"])
@pytest.mark.parametrize(
    "value, expected",
    [
        (
            datetime(2026, 1, 2, 3, 4, 5, 123456, tzinfo=timezone.utc),
            "datetime('2026-01-02T03:04:05.123456+00:00')",
        ),
        (
            datetime(2026, 1, 2, 3, 4, 5, 123456, tzinfo=timezone(timedelta(hours=5, minutes=30))),
            "datetime('2026-01-02T03:04:05.123456+05:30')",
        ),
        (
            datetime(2026, 11, 1, 1, 30, 0, 123456, tzinfo=ZoneInfo("America/New_York"), fold=0),
            "datetime('2026-11-01T01:30:00.123456-04:00[America/New_York]')",
        ),
        (
            datetime(2026, 11, 1, 1, 30, 0, 123456, tzinfo=ZoneInfo("America/New_York"), fold=1),
            "datetime('2026-11-01T01:30:00.123456-05:00[America/New_York]')",
        ),
        (
            datetime(2026, 1, 2, 3, 4, 5, 123456, tzinfo=pytz.UTC),
            "datetime('2026-01-02T03:04:05.123456Z')",
        ),
        (
            pytz.timezone("America/Los_Angeles").localize(datetime(2026, 1, 2, 3, 4, 5, 123456)),
            "datetime('2026-01-02T03:04:05.123456-08:00[America/Los_Angeles]')",
        ),
        (datetime(2026, 1, 2, 3, 4, 5, 123456), "localDateTime('2026-01-02T03:04:05.123456')"),
        (datetime(2026, 1, 2, 3, 4, 5), "localDateTime('2026-01-02T03:04:05')"),
    ],
)
def test_datetime_serialization(value, expected, serializer):
    assert serializer(value) == expected
