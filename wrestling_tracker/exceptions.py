"""
Wrestling Match Tracker
Author: Aayush Pande
Purpose: Defines the focused exception types raised by the tracker so that
    callers can handle each kind of failure separately: invalid match data
    and storage failures.
Starter Code/Resources: None
Date: 2026-11-03
"""


class MatchValidationError(ValueError):
    """Raised when match data is invalid (bad name, bad score, or a tie).

    It subclasses ValueError because the problem is always an unacceptable
    value, which lets generic callers treat it as one if they wish.
    """


class DataPersistenceError(Exception):
    """Raised when match data cannot be read from or written to storage.

    It covers filesystem failures, malformed JSON, and stored records that are
    not valid matches. The original exception is kept as __cause__ so the
    underlying reason is not lost.
    """
