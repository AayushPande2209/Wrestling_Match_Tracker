"""
Wrestling Match Tracker
Author: Aayush Pande
Purpose: Defines the focused exception types raised by the tracker so that
    callers can handle each kind of failure separately.
Starter Code/Resources: None
Date: 2026-11-03
"""


class MatchValidationError(ValueError):
    """Raised when match data is invalid (bad name, bad score, or a tie).

    It subclasses ValueError because the problem is always an unacceptable
    value, which lets generic callers treat it as one if they wish.
    """
