# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from datetime import timedelta

import factory

from _mocks.temporal import get_mock_utcnow


class TimestampsEntityFactoryMixin(factory.Factory):
    created_at = get_mock_utcnow()
    updated_at = get_mock_utcnow() + timedelta(minutes=30)
