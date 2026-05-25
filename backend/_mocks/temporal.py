from __future__ import annotations

from datetime import datetime, timezone


def get_mock_utcnow() -> datetime:
    """Returns a mock UTC datetime for testing purposes."""
    return datetime(2026, 4, 20, 11, 15, 0, tzinfo=timezone.utc)


def get_may_the_4th_be_with_you_utcnow() -> datetime:
    """
    Returns a mock UTC datetime for testing purposes.

    May the 4th be with you, always.
    """
    return datetime(2026, 5, 4, 11, 15, 0, tzinfo=timezone.utc)
