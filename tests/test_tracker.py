"""
Wrestling Match Tracker
Author: Aayush Pande
Purpose: Tests for SeasonTracker: history, composition, statistics, and
    opponent search.
Starter Code/Resources: None
Date: 2026-11-04
"""

import pytest

from wrestling_tracker.match import WrestlingMatch
from wrestling_tracker.tracker import SeasonTracker


@pytest.fixture
def three_match_tracker():
    """Return a tracker with John 8-4 (W), Mike 3-5 (L), Alex 10-2 (W)."""
    return SeasonTracker(
        [
            WrestlingMatch("John Smith", 8, 4),
            WrestlingMatch("Mike Davis", 3, 5),
            WrestlingMatch("Alex Brown", 10, 2),
        ]
    )


class TestHistoryAndComposition:
    """The tracker owns its matches but does not expose its own list."""

    def test_new_tracker_is_empty(self):
        """A tracker created without matches has no history."""
        assert SeasonTracker().get_history() == []

    def test_add_match_appends_in_order(self, winning_match, losing_match):
        """Matches come back in the order they were added."""
        tracker = SeasonTracker()
        tracker.add_match(winning_match)
        tracker.add_match(losing_match)
        assert tracker.get_history() == [winning_match, losing_match]

    def test_constructor_accepts_existing_matches(
        self, winning_match, losing_match
    ):
        """Loaded matches can be passed in when the tracker is created."""
        tracker = SeasonTracker([winning_match, losing_match])
        assert tracker.get_history() == [winning_match, losing_match]

    def test_constructor_copies_the_given_list(self, winning_match):
        """Changing the list passed in later does not change the tracker."""
        starting_matches = [winning_match]
        tracker = SeasonTracker(starting_matches)
        starting_matches.clear()
        assert tracker.get_history() == [winning_match]

    def test_history_is_a_copy(self, season_tracker):
        """Editing the returned list cannot corrupt the tracker."""
        history = season_tracker.get_history()
        history.clear()
        assert len(season_tracker.get_history()) == 2

    @pytest.mark.parametrize(
        "not_a_match",
        [{"opponent_name": "A", "wrestler_score": 2, "opponent_score": 1},
         "John Smith", None, 5],
    )
    def test_only_wrestling_matches_can_be_added(self, not_a_match):
        """Dictionaries and other objects are rejected."""
        tracker = SeasonTracker()
        with pytest.raises(TypeError):
            tracker.add_match(not_a_match)
        assert tracker.get_history() == []

    def test_tracker_has_matches_but_is_not_a_match(self, season_tracker):
        """Composition: the tracker contains matches; it is not one."""
        assert not isinstance(season_tracker, WrestlingMatch)
        assert all(
            isinstance(match, WrestlingMatch)
            for match in season_tracker.get_history()
        )


class TestStatistics:
    """Statistics are calculated from the stored matches."""

    def test_empty_statistics_are_all_zero(self):
        """No matches means zeros, not a division-by-zero error."""
        assert SeasonTracker().get_statistics() == {
            "total_matches": 0,
            "wins": 0,
            "losses": 0,
            "win_percentage": 0.0,
            "total_points": 0,
            "average_points": 0.0,
        }

    def test_known_season(self, three_match_tracker):
        """Hand-calculated values: 3 matches, 2-1, 66.7%, 21 points, 7.0."""
        statistics = three_match_tracker.get_statistics()
        assert statistics["total_matches"] == 3
        assert statistics["wins"] == 2
        assert statistics["losses"] == 1
        assert statistics["win_percentage"] == pytest.approx(66.6667, abs=1e-3)
        assert statistics["total_points"] == 21
        assert statistics["average_points"] == pytest.approx(7.0)

    def test_all_losses(self):
        """A winless season is 0% with the points still counted."""
        tracker = SeasonTracker(
            [WrestlingMatch("A", 0, 1), WrestlingMatch("B", 2, 9)]
        )
        statistics = tracker.get_statistics()
        assert statistics["wins"] == 0
        assert statistics["losses"] == 2
        assert statistics["win_percentage"] == 0.0
        assert statistics["total_points"] == 2
        assert statistics["average_points"] == pytest.approx(1.0)

    def test_all_wins(self):
        """An undefeated season is 100%."""
        tracker = SeasonTracker([WrestlingMatch("A", 5, 0)])
        assert tracker.get_statistics()["win_percentage"] == 100.0

    def test_statistics_update_when_a_match_is_added(
        self, three_match_tracker
    ):
        """Adding a 6-0 win makes it 4 matches, 3-1, 75%, 27 points, 6.75."""
        three_match_tracker.add_match(WrestlingMatch("Chris", 6, 0))
        statistics = three_match_tracker.get_statistics()
        assert statistics["total_matches"] == 4
        assert statistics["wins"] == 3
        assert statistics["losses"] == 1
        assert statistics["win_percentage"] == pytest.approx(75.0)
        assert statistics["total_points"] == 27
        assert statistics["average_points"] == pytest.approx(6.75)

    def test_wins_and_losses_always_add_up(self, three_match_tracker):
        """Every match is counted exactly once as a win or a loss."""
        statistics = three_match_tracker.get_statistics()
        assert statistics["wins"] + statistics["losses"] == (
            statistics["total_matches"]
        )

    def test_only_the_wrestlers_points_are_counted(self):
        """Opponent points are not part of "points scored"."""
        tracker = SeasonTracker([WrestlingMatch("A", 2, 100)])
        assert tracker.get_statistics()["total_points"] == 2


class TestSearch:
    """Opponent search is case-insensitive and accepts partial names."""

    @pytest.mark.parametrize(
        "search_text", ["John Smith", "john smith", "JOHN SMITH", "JoHn SmItH"]
    )
    def test_search_ignores_capitalization(
        self, three_match_tracker, search_text
    ):
        """Any capitalization finds the same opponent."""
        results = three_match_tracker.search_opponents(search_text)
        assert [match.opponent_name for _, match in results] == ["John Smith"]

    @pytest.mark.parametrize("search_text", ["john", "smith", "n sm", "h"])
    def test_search_accepts_partial_names(
        self, three_match_tracker, search_text
    ):
        """A fragment anywhere in the name matches."""
        results = three_match_tracker.search_opponents(search_text)
        assert "John Smith" in [match.opponent_name for _, match in results]

    def test_search_with_no_result_returns_empty_list(
        self, three_match_tracker
    ):
        """An unknown opponent gives an empty list, not an error."""
        assert three_match_tracker.search_opponents("Zed") == []

    def test_search_on_empty_tracker_returns_empty_list(self):
        """Searching with no matches recorded finds nothing."""
        assert SeasonTracker().search_opponents("john") == []

    def test_results_keep_their_history_position(self, three_match_tracker):
        """Match numbers match the full history (starting at 1)."""
        results = three_match_tracker.search_opponents("brown")
        assert [match_number for match_number, _ in results] == [3]

    def test_rematches_are_all_returned_in_order(self, three_match_tracker):
        """Every match against the same opponent appears, oldest first."""
        three_match_tracker.add_match(WrestlingMatch("John Smith", 1, 2))
        results = three_match_tracker.search_opponents("JOHN")
        assert [match_number for match_number, _ in results] == [1, 4]
        assert [match.result for _, match in results] == ["Win", "Loss"]

    def test_search_text_is_stripped(self, three_match_tracker):
        """Surrounding spaces in the search text are ignored."""
        results = three_match_tracker.search_opponents("  mike  ")
        assert len(results) == 1

    @pytest.mark.parametrize("blank_text", ["", "   ", "\t"])
    def test_blank_search_is_rejected(self, three_match_tracker, blank_text):
        """A blank search would match everything, so it is an error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            three_match_tracker.search_opponents(blank_text)
