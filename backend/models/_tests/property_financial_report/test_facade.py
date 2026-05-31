from __future__ import annotations

from datetime import datetime

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
            if key == "calculated_at":
                expected_dt = datetime.fromisoformat(value).replace(tzinfo=None)
                assert result.calculated_at == expected_dt
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
