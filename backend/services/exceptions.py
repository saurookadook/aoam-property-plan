from __future__ import annotations


class ScrapeError(Exception):
    """Base for any failure while sourcing a property from a listing site."""


class FetchError(ScrapeError):
    """Raised when a listing page could not be retrieved."""


class UnsupportedSource(ScrapeError):
    """Raised when no parser is registered for a listing URL's host."""
