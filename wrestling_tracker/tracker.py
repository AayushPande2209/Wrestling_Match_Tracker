"""
Wrestling Match Tracker
Author: Aayush Pande
Purpose: Defines SeasonTracker, which owns the season's matches and answers
    questions about them (history, search, statistics).
Starter Code/Resources: None
Date: 2026-11-03
"""

from wrestling_tracker.match import WrestlingMatch


class SeasonTracker:
    """A season's collection of WrestlingMatch objects.

    SeasonTracker uses composition: it *has* matches, it is not a kind of
    match. It never prints or reads input; it returns data and leaves
    presentation to the command-line interface.
    """

    def __init__(self, matches=None):
        """Create a tracker, optionally starting with existing matches.

        Args:
            matches: An optional iterable of WrestlingMatch objects, for
                example the ones loaded from storage.
        """
        self._matches = []
        if matches is not None:
            for match in matches:
                self.add_match(match)

    def add_match(self, match):
        """Add one match to the end of the season.

        Args:
            match: The WrestlingMatch to add.

        Raises:
            TypeError: If match is not a WrestlingMatch.
        """
        if not isinstance(match, WrestlingMatch):
            raise TypeError("Only WrestlingMatch objects can be added.")
        self._matches.append(match)

    def get_history(self):
        """Return a new list of all matches in the order they were added.

        A copy is returned so callers cannot change the tracker's own list.
        """
        return list(self._matches)

    def search_opponents(self, search_text):
        """Find matches whose opponent name contains the search text.

        The search ignores capitalization and accepts partial names, so
        "john" finds "John Smith".

        Args:
            search_text: Full or partial opponent name; must not be blank.

        Returns:
            A list of (match_number, match) tuples in season order. The
            match number is the position in the full history (starting at 1)
            so results line up with the history display.

        Raises:
            ValueError: If search_text is blank.
        """
        wanted_text = search_text.strip().lower()
        if wanted_text == "":
            raise ValueError("Search text cannot be empty.")

        results = []
        for match_number, match in enumerate(self._matches, start=1):
            if wanted_text in match.opponent_name.lower():
                results.append((match_number, match))
        return results

    def get_statistics(self):
        """Calculate season statistics from the recorded matches.

        Returns:
            A dictionary with the keys "total_matches", "wins", "losses",
            "win_percentage", "total_points", and "average_points". With no
            matches every value is 0, so callers never divide by zero.
        """
        total_matches = len(self._matches)
        wins = 0
        total_points = 0
        for match in self._matches:
            if match.result == "Win":
                wins += 1
            total_points += match.wrestler_score

        if total_matches == 0:
            win_percentage = 0.0
            average_points = 0.0
        else:
            win_percentage = wins / total_matches * 100
            average_points = total_points / total_matches

        return {
            "total_matches": total_matches,
            "wins": wins,
            "losses": total_matches - wins,
            "win_percentage": win_percentage,
            "total_points": total_points,
            "average_points": average_points,
        }
