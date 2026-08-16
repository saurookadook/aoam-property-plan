"""
Colombia operating assumptions - the defaults the calculation engine runs on.

Every value here is a row of Part 6 of ``docs/COLOMBIA_STR_EXECUTION_PLAN_v3.md``,
kept in one module so the analysis form (Step 8) can serve the same numbers the
maths uses. ``constants/__init__.py`` is deliberately not the home for these: it
holds terminal-geometry and base-URL odds and ends, and mixing domain assumptions
into it would leave no obvious place to look when a rate changes.

Percentages are whole numbers - ``10.0`` means 10%, matching the ``NUMERIC``
columns on ``property_financial_reports`` and the model fixtures. Money is COP and
``float``, never ``Decimal``.
"""

from __future__ import annotations

DEFAULT_INTEREST_RATE_PERCENTAGE = 10.0
"""
Part 6: \"Mortgage interest rate\" - midpoint of the typical 9-12% COP-denominated
range offered to foreign buyers.
"""

DEFAULT_DOWN_PAYMENT_PERCENTAGE = 30.0
"""
Part 6: \"Down payment\" - deliberately conservative; some banks accept 20%.
"""

DEFAULT_LOAN_TERM_YEARS = 15
"""
Part 6: \"Loan term\" - standard for Colombian investment property.
"""

DEFAULT_MANAGEMENT_FEE_PERCENTAGE = 22.0
"""
Part 6: \"Property management fee\" - of *gross* revenue, not net. Typical range
is 18-25% and includes cleaning coordination.
"""

DEFAULT_MAINTENANCE_RESERVE_PERCENTAGE = 1.0
"""
Part 6: \"Maintenance reserve\" - of purchase price, per year.
"""

DEFAULT_CLOSING_COSTS_PERCENTAGE = 2.75
"""
Part 6: \"Closing costs\" - of purchase price, one-off. Notary fees, registration
taxes and escritura; the 2.5-3% range midpoint.
"""

DEFAULT_PREDIAL_RATE_PERCENTAGE = 0.8
"""
Part 6: \"Predial (property tax)\" - of assessed value, per year. Ranges 0.5-1.5%
by city, with urban Bogota toward the top.
"""

HOA_MONTHLY_COP_BY_CITY = {
    "Bogota": 500_000.0,
    "Medellin": 500_000.0,
    "Cali": 300_000.0,
}
"""
Part 6: \"HOA (administracion) - urban apartments\". The row quotes a COP 350,000
midpoint over a COP 200K-1.2M range, then pre-populates by city; these are those
city figures. Lookups that miss fall back to DEFAULT_HOA_MONTHLY_COP.
"""

DEFAULT_HOA_MONTHLY_COP = 0.0
"""
Part 6: \"HOA - Calima / Pance / Salento fincas\". Standalone rural property has no
administracion at all, which is a real cost advantage over urban apartments - so
zero is the default rather than the urban midpoint.
"""

MONTHS_PER_YEAR = 12
"""
Named so the annual-to-monthly conversions read as conversions rather than as a
bare literal repeated at every call site.
"""
