"""WorklogCreate fills in the start Tracker requires."""

import re

from ycli.yandex.tracker.worklog.models import WorklogCreate


def test_a_time_report_without_a_start_starts_now():
    """Tracker refuses a report without ``start`` (422), so the model uses the current time."""
    start = WorklogCreate(duration="PT1H").start
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}[+-]\d{4}", start)
