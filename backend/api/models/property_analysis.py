from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional, cast

from pydantic import BaseModel, ConfigDict, create_model
from pydantic.fields import FieldInfo

from models.property_comp.entity import PropertyCompWithListingEntity
from models.property_financial_report.entity import PropertyFinancialReportEntity
from services.calculations import (
    MonthlyExpenseBreakdown,
    PropertyScenario,
    SensitivityCell,
)
from utils.pydantic_helpers import BaseResponseModel

# Derived by the analysis rather than supplied: the revenue estimate is the whole
# point of the call, and the exchange rate has to come off ``exchange_rates`` so
# that one rate explains every ``_usd`` figure in the report.
DERIVED_FIELDS = ("annual_revenue_cop", "cop_per_usd")


def _optional_scenario_fields() -> dict[str, tuple[Any, FieldInfo]]:
    """
    Every ``PropertyScenario`` knob, made optional and stripped of its default.

    Read off ``PropertyScenario`` rather than redeclared so the two cannot drift:
    adding an assumption to the calculation engine exposes it here automatically,
    with its bounds intact - ``down_payment_percentage=140`` is rejected at the
    edge of the API rather than deep inside ``analyze()``.

    The defaults are deliberately dropped. ``PropertyScenario`` already owns them,
    and copying them into the request model would mean an omitted field arrived as
    a value the caller never chose, making "unset" indistinguishable from
    "explicitly the Part 6 default".
    """
    fields: dict[str, tuple[Any, FieldInfo]] = {}

    for name, field in PropertyScenario.model_fields.items():
        if name in DERIVED_FIELDS:
            continue

        optional_field = deepcopy(field)
        optional_field.default = None
        optional_field.default_factory = None

        fields[name] = (Optional[field.annotation], optional_field)

    return fields


class ScenarioOverridesRequest(BaseModel):
    """Base for the generated request model - see ``PropertyAnalyzeRequest``."""

    # An unrecognised key is a 422 rather than a silent omission. The trap this
    # closes: ``property_financial_reports`` stores the interest rate in a column
    # called ``interest_rate``, so seeding a re-analysis form from a stored report
    # and posting it straight back sends ``interest_rate``, which is not a
    # scenario field. Ignored, the request would quietly run at the 10% default
    # and hand back a number the caller never asked for.
    model_config = ConfigDict(extra="forbid")

    def overrides(self) -> dict[str, Any]:
        """
        Only what the caller actually supplied.

        ``exclude_none`` rather than a truthiness test, so that an explicit
        ``hoa_monthly_cop`` of ``0`` reaches the scenario instead of silently
        falling back to the city default.
        """
        return self.model_dump(exclude_none=True)


PropertyAnalyzeRequest = create_model(
    "PropertyAnalyzeRequest",
    __base__=ScenarioOverridesRequest,
    __doc__=(
        "Assumptions to analyse a property under. Every field is optional; "
        "anything omitted falls back to the Colombia defaults in "
        "``constants.colombia``, so an empty body is a valid request.\n\n"
        "``purchase_price_cop`` is accepted because a property whose listing hid "
        "its price has none stored, and the analysis cannot run without one."
    ),
    **cast(dict[str, Any], _optional_scenario_fields()),
)


class PropertyAnalysisData(BaseResponseModel):
    """
    A report plus the two things it implies but does not store.

    ``expenses`` and ``sensitivity`` are computed from the report's own inputs
    rather than persisted. Columns for either would freeze a presentation choice
    into the schema - ``DEFAULT_SENSITIVITY_FACTORS`` is a decision about what to
    show, not a fact about the property - and would save nothing on the read
    path, since every input the arithmetic needs is already on the row.
    """

    report: PropertyFinancialReportEntity
    expenses: MonthlyExpenseBreakdown
    sensitivity: list[SensitivityCell]


class PropertyAnalysisResponse(BaseResponseModel):
    data: PropertyAnalysisData


class PropertyAnalysisReportResponse(BaseResponseModel):
    """
    The latest stored analysis, or ``None`` for a property never analysed.

    ``null`` with a 200 rather than a 404, matching ``/comps/cached``: the
    property exists and the honest answer to "what does its report say" is
    "nothing yet".
    """

    data: Optional[PropertyAnalysisData] = None


class PropertyCompsResponse(BaseResponseModel):
    data: list[PropertyCompWithListingEntity]
