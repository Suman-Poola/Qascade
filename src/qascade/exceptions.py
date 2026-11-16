"""Exception types raised by Qascade."""

from __future__ import annotations

__all__ = ["BudgetExceededError", "NotSupportedError", "QascadeError"]


class QascadeError(Exception):
    """Base class for all errors raised by Qascade."""


class NotSupportedError(QascadeError):
    """A circuit, gate or option is not supported by the chosen engine or method.

    The message names the offending object and says what to use instead.
    """


class BudgetExceededError(QascadeError):
    """A circuit-execution budget was exhausted before the requested work could finish."""
