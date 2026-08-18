from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from _factories.property_financial_report.db import (
    PropertyFinancialReportDBFactory,
)
from models.property_financial_report.entity import (
    PropertyFinancialReportEntity,
)
from models.property_financial_report.facade import (
    PropertyFinancialReportFacade,
)


class TestPropertyFinancialReportFacade:
    @pytest.fixture
    def property_financial_report_facade(self, test_db_session):
        return PropertyFinancialReportFacade(db_session=test_db_session)

    @pytest.fixture
    def property_financial_report_record(
        self, expected_property_financial_report_dict, test_db_session
    ):
        property_financial_report = PropertyFinancialReportDBFactory(
            **expected_property_financial_report_dict
        )
        test_db_session.commit()
        return property_financial_report

    def _compare_result_with_expected(
        self,
        result: PropertyFinancialReportEntity,
        expected_dict: dict,
    ):
        for key, value in expected_dict.items():
            # ``calculated_at`` alone arrives as an ISO string rather than a
            # datetime, so it is compared parsed. The offset it carries is
            # significant now that the column is ``TIMESTAMP(timezone=True)`` -
            # it used to be dropped on the way into the database.
            if key == "calculated_at":
                assert result.calculated_at == datetime.fromisoformat(value)
            else:
                assert getattr(result, key) == value

        return True

    def test_get_one_by_id(
        self,
        property_financial_report_facade,
        property_financial_report_record,
    ):
        result = property_financial_report_facade.get_one_by_id(
            property_financial_report_record.id
        )
        assert result == PropertyFinancialReportEntity.model_validate(
            property_financial_report_record
        )

    def test_get_one_by_id_no_result(self, property_financial_report_facade):
        with pytest.raises(PropertyFinancialReportFacade.NoResultFound):
            non_existent_id = "988d0b5d-d4a5-4808-a94d-2d9df1df7588"
            property_financial_report_facade.get_one_by_id(non_existent_id)

    def test_create_or_update_creates_new_record(
        self,
        property_financial_report_facade,
        expected_property_financial_report_dict,
    ):
        result = property_financial_report_facade.create_or_update(
            payload=expected_property_financial_report_dict
        )

        assert self._compare_result_with_expected(
            result, expected_property_financial_report_dict
        )

    def test_create_or_update_updates_existing_record(
        self,
        property_financial_report_facade,
        property_financial_report_record,
    ):
        property_financial_report_entity = PropertyFinancialReportEntity.model_validate(
            property_financial_report_record
        )
        property_financial_report_dict = property_financial_report_entity.model_dump()
        updated_payload = {
            **property_financial_report_dict,
            "calculated_at": (
                property_financial_report_entity.calculated_at.isoformat()
            ),
            "loan_term_years": (property_financial_report_dict["loan_term_years"] + 5),
        }

        result = property_financial_report_facade.create_or_update(
            payload=updated_payload
        )

        assert self._compare_result_with_expected(result, updated_payload)
        assert (
            result.loan_term_years != property_financial_report_dict["loan_term_years"]
        )

    def test_get_latest_by_property_id_returns_none_when_never_analysed(
        self, property_financial_report_facade, property_record
    ):
        assert (
            property_financial_report_facade.get_latest_by_property_id(
                property_record.id
            )
            is None
        )

    def test_get_latest_by_property_id(
        self,
        property_financial_report_facade,
        mock_utcnow,
        property_record,
        test_db_session,
    ):
        older = PropertyFinancialReportDBFactory(
            property_id=property_record.id,
            calculated_at=mock_utcnow - timedelta(days=10),
        )
        newest = PropertyFinancialReportDBFactory(
            property_id=property_record.id,
            calculated_at=mock_utcnow - timedelta(days=1),
        )
        # Postgres sorts nulls *first* under ``DESC``, so without ``nullslast()``
        # a report that was never stamped would outrank every real one.
        undated = PropertyFinancialReportDBFactory(
            property_id=property_record.id, calculated_at=None
        )
        test_db_session.commit()

        result = property_financial_report_facade.get_latest_by_property_id(
            property_record.id
        )

        assert result is not None
        assert result.id == newest.id
        assert result.id not in (older.id, undated.id)
