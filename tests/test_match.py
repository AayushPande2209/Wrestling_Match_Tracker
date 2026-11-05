"""
Wrestling Match Tracker
Author: Aayush Pande
Purpose: Tests for WrestlingMatch: validation, the derived result, and
    dictionary serialization.
Starter Code/Resources: None
Date: 2026-11-04
"""

import pytest

from wrestling_tracker.exceptions import MatchValidationError
from wrestling_tracker.match import (
    WrestlingMatch,
    validate_opponent_name,
    validate_score,
)


class TestDerivedResult:
    """The result is calculated from the scores, never supplied."""

    def test_higher_wrestler_score_is_a_win(self):
        """A higher wrestler score gives "Win"."""
        assert WrestlingMatch("A", 8, 4).result == "Win"

    def test_lower_wrestler_score_is_a_loss(self):
        """A lower wrestler score gives "Loss"."""
        assert WrestlingMatch("A", 3, 5).result == "Loss"

    def test_zero_points_can_still_win_or_lose(self):
        """A shutout (a score of 0) is valid for either side."""
        assert WrestlingMatch("A", 5, 0).result == "Win"
        assert WrestlingMatch("A", 0, 5).result == "Loss"

    def test_attributes_are_stored(self):
        """The constructor keeps the name and both scores."""
        match = WrestlingMatch("John Smith", 8, 4)
        assert match.opponent_name == "John Smith"
        assert match.wrestler_score == 8
        assert match.opponent_score == 4

    def test_name_is_stripped(self):
        """Surrounding spaces are removed from the opponent name."""
        assert WrestlingMatch("  John Smith  ", 8, 4).opponent_name == (
            "John Smith"
        )

    @pytest.mark.parametrize(
        "attribute",
        ["opponent_name", "wrestler_score", "opponent_score", "result"],
    )
    def test_attributes_are_read_only(self, attribute):
        """A valid match cannot be made invalid by assigning to it later."""
        match = WrestlingMatch("A", 8, 4)
        with pytest.raises(AttributeError):
            setattr(match, attribute, "changed")


class TestValidation:
    """Invalid input is rejected with MatchValidationError."""

    @pytest.mark.parametrize("bad_name", ["", "   ", "\t\n"])
    def test_empty_or_blank_name_is_rejected(self, bad_name):
        """Empty and whitespace-only names are rejected."""
        with pytest.raises(MatchValidationError, match="cannot be empty"):
            WrestlingMatch(bad_name, 8, 4)

    @pytest.mark.parametrize("bad_name", [None, 42, ["John"], b"John"])
    def test_non_string_name_is_rejected(self, bad_name):
        """Names that are not text are rejected."""
        with pytest.raises(MatchValidationError, match="must be text"):
            WrestlingMatch(bad_name, 8, 4)

    @pytest.mark.parametrize("bad_score", [True, False])
    def test_boolean_scores_are_rejected(self, bad_score):
        """bool is a subclass of int, but True/False are not real scores."""
        with pytest.raises(MatchValidationError, match="whole number"):
            WrestlingMatch("A", bad_score, 0)
        with pytest.raises(MatchValidationError, match="whole number"):
            WrestlingMatch("A", 5, bad_score)

    @pytest.mark.parametrize("bad_score", [1.5, 3.0, "3", None, [3], (3,)])
    def test_non_integer_scores_are_rejected(self, bad_score):
        """Floats (even 3.0), strings, None, and containers are rejected."""
        with pytest.raises(MatchValidationError, match="whole number"):
            WrestlingMatch("A", bad_score, 1)
        with pytest.raises(MatchValidationError, match="whole number"):
            WrestlingMatch("A", 9, bad_score)

    @pytest.mark.parametrize("bad_score", [-1, -100])
    def test_negative_scores_are_rejected(self, bad_score):
        """Negative scores are rejected for either side."""
        with pytest.raises(MatchValidationError, match="cannot be negative"):
            WrestlingMatch("A", bad_score, 1)
        with pytest.raises(MatchValidationError, match="cannot be negative"):
            WrestlingMatch("A", 9, bad_score)

    @pytest.mark.parametrize("tied_score", [0, 1, 7])
    def test_ties_are_rejected(self, tied_score):
        """Wrestling matches have a winner, so equal scores are rejected."""
        with pytest.raises(MatchValidationError, match="tie"):
            WrestlingMatch("A", tied_score, tied_score)

    def test_validation_error_is_a_value_error(self):
        """Generic ValueError handlers also catch validation failures."""
        with pytest.raises(ValueError):
            WrestlingMatch("", 1, 0)

    def test_validate_helpers_return_clean_values(self):
        """The helper functions return the accepted value."""
        assert validate_opponent_name("  Ann ") == "Ann"
        assert validate_score(0) == 0


class TestSerialization:
    """to_dict() and from_dict() convert to and from plain dictionaries."""

    def test_to_dict_contains_only_the_input_fields(self, winning_match):
        """The derived result is not stored in the dictionary."""
        assert winning_match.to_dict() == {
            "opponent_name": "John Smith",
            "wrestler_score": 8,
            "opponent_score": 4,
        }

    def test_round_trip_preserves_the_match(self, winning_match, losing_match):
        """from_dict(to_dict(match)) equals the original, result included."""
        for original in (winning_match, losing_match):
            restored = WrestlingMatch.from_dict(original.to_dict())
            assert restored == original
            assert restored.result == original.result

    def test_stored_result_cannot_override_the_scores(self):
        """A tampered "result" entry is ignored; the scores decide."""
        match_data = {
            "opponent_name": "A",
            "wrestler_score": 1,
            "opponent_score": 9,
            "result": "Win",
        }
        assert WrestlingMatch.from_dict(match_data).result == "Loss"

    @pytest.mark.parametrize("not_a_dict", [None, [], "match", 5, [("a", 1)]])
    def test_from_dict_rejects_non_dictionaries(self, not_a_dict):
        """Anything other than a dictionary is not a match record."""
        with pytest.raises(MatchValidationError, match="dictionary"):
            WrestlingMatch.from_dict(not_a_dict)

    @pytest.mark.parametrize(
        "missing_field", ["opponent_name", "wrestler_score", "opponent_score"]
    )
    def test_from_dict_rejects_missing_fields(self, missing_field):
        """Each required field must be present."""
        match_data = {
            "opponent_name": "A",
            "wrestler_score": 8,
            "opponent_score": 4,
        }
        del match_data[missing_field]
        with pytest.raises(MatchValidationError, match=missing_field):
            WrestlingMatch.from_dict(match_data)

    @pytest.mark.parametrize(
        "bad_record",
        [
            {"opponent_name": "", "wrestler_score": 8, "opponent_score": 4},
            {"opponent_name": "A", "wrestler_score": "8", "opponent_score": 4},
            {"opponent_name": "A", "wrestler_score": -8, "opponent_score": 4},
            {"opponent_name": "A", "wrestler_score": 4, "opponent_score": 4},
            {"opponent_name": "A", "wrestler_score": True,
             "opponent_score": 0},
        ],
    )
    def test_from_dict_validates_values(self, bad_record):
        """Stored values go through the same validation as new matches."""
        with pytest.raises(MatchValidationError):
            WrestlingMatch.from_dict(bad_record)


class TestEquality:
    """Matches with the same data are equal."""

    def test_equal_when_all_fields_match(self):
        """Same name and scores means equal."""
        assert WrestlingMatch("A", 8, 4) == WrestlingMatch("A", 8, 4)

    def test_not_equal_when_any_field_differs(self):
        """A different name or score means not equal."""
        base = WrestlingMatch("A", 8, 4)
        assert base != WrestlingMatch("B", 8, 4)
        assert base != WrestlingMatch("A", 9, 4)
        assert base != WrestlingMatch("A", 8, 3)

    def test_not_equal_to_other_types(self):
        """A match never equals its dictionary form."""
        match = WrestlingMatch("A", 8, 4)
        assert match != match.to_dict()
