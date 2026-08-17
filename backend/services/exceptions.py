from __future__ import annotations


class ScrapeError(Exception):
    """Base for any failure while sourcing a property from a listing site."""


class FetchError(ScrapeError):
    """Raised when a listing page could not be retrieved."""


class UnsupportedSource(ScrapeError):
    """Raised when no parser is registered for a listing URL's host."""


class AirROIError(Exception):
    """
    Raised when a call to the AirROI API fails or comes back unusable.

    Deliberately not a ``ScrapeError``: that hierarchy is about sourcing a
    property from a listing site, and callers of the two are different - a route
    turns ``ScrapeError`` into a 422 and ``AirROIError`` into a 502.
    """
