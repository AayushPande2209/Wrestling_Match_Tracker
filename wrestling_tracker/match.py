"""
Wrestling Match Tracker
Author: Aayush Pande
Purpose: Defines WrestlingMatch, the domain object for one completed match,
    together with the validation rules for names and scores.
Starter Code/Resources: None
Date: 2026-11-03
"""

from wrestling_tracker.exceptions import MatchValidationError


def validate_opponent_name(opponent_name):
    """Return the opponent name without surrounding spaces.

    Args:
        opponent_name: The name to check.

    Returns:
        The stripped name.

    Raises:
        MatchValidationError: If the value is not a string or is empty
            after stripping.
    """
    if not isinstance(opponent_name, str):
        raise MatchValidationError("Opponent name must be text.")
    cleaned_name = opponent_name.strip()
    if cleaned_name == "":
        raise MatchValidationError("Opponent name cannot be empty.")
    return cleaned_name


def validate_score(score):
    """Return the score if it is a non-negative whole number.

    Args:
        score: The score to check.

    Returns:
        The same score, unchanged.

    Raises:
        MatchValidationError: If the score is not an int or is negative.
    """
    # bool is a subclass of int, so True would otherwise pass as the score 1.
    if isinstance(score, bool) or not isinstance(score, int):
        raise MatchValidationError("Score must be a whole number.")
    if score < 0:
        raise MatchValidationError("Score cannot be negative.")
    return score


class WrestlingMatch:
    """One completed wrestling match.

    The fields are validated when the object is created and exposed as
    read-only properties, so a WrestlingMatch can never hold invalid data.
    The result is derived from the scores rather than stored, which means it
    can never disagree with them.
    """

    def __init__(self, opponent_name, wrestler_score, opponent_score):
        """Create a match after validating every field.

        Args:
            opponent_name: Name of the opponent; must not be empty.
            wrestler_score: Points scored by the user; a non-negative int.
            opponent_score: Points scored by the opponent; a non-negative int.

        Raises:
            MatchValidationError: If any value is invalid or the scores tie.
        """
        self._opponent_name = validate_opponent_name(opponent_name)
        self._wrestler_score = validate_score(wrestler_score)
        self._opponent_score = validate_score(opponent_score)
        if self._wrestler_score == self._opponent_score:
            raise MatchValidationError(
                "Matches cannot end in a tie. Match not recorded."
            )

    @property
    def opponent_name(self):
        """Return the opponent's name."""
        return self._opponent_name

    @property
    def wrestler_score(self):
        """Return the points scored by the user."""
        return self._wrestler_score

    @property
    def opponent_score(self):
        """Return the points scored by the opponent."""
        return self._opponent_score

    @property
    def result(self):
        """Return "Win" or "Loss", calculated from the two scores."""
        if self._wrestler_score > self._opponent_score:
            return "Win"
        return "Loss"

    def to_dict(self):
        """Return the match as a dictionary that can be stored as JSON.

        The result is left out on purpose because it is derived from the
        scores when the match is loaded again.
        """
        return {
            "opponent_name": self._opponent_name,
            "wrestler_score": self._wrestler_score,
            "opponent_score": self._opponent_score,
        }

    @classmethod
    def from_dict(cls, match_data):
        """Build a match from a dictionary created by to_dict().

        Args:
            match_data: A dictionary with the keys "opponent_name",
                "wrestler_score", and "opponent_score".

        Returns:
            A new, fully validated WrestlingMatch.

        Raises:
            MatchValidationError: If match_data is not a dictionary, a key is
                missing, or a value is invalid.
        """
        if not isinstance(match_data, dict):
            raise MatchValidationError("A match record must be a dictionary.")
        try:
            return cls(
                match_data["opponent_name"],
                match_data["wrestler_score"],
                match_data["opponent_score"],
            )
        except KeyError as error:
            raise MatchValidationError(
                f"Match record is missing the field {error}."
            ) from error

    def __eq__(self, other):
        """Return True if both matches have identical names and scores."""
        if not isinstance(other, WrestlingMatch):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __repr__(self):
        """Return an unambiguous text form, useful in test failures."""
        return (
            f"WrestlingMatch(opponent_name={self._opponent_name!r}, "
            f"wrestler_score={self._wrestler_score}, "
            f"opponent_score={self._opponent_score})"
        )
