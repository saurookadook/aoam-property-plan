from __future__ import annotations

import factory

from _mocks.temporal import get_mock_utcnow


class TimestampsDBMixinFactory(factory.alchemy.SQLAlchemyModelFactory):
    created_at = get_mock_utcnow()
    updated_at = get_mock_utcnow()
