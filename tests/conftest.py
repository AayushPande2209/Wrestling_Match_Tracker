"""
Wrestling Match Tracker
Author: Aayush Pande
Purpose: Shared pytest fixtures. They provide sample matches and temporary
    storage, and guarantee that no test can touch the real data/matches.json.
Starter Code/Resources: None
Date: 2026-11-04
"""

import pytest

from wrestling_tracker import cli
from wrestling_tracker.match import WrestlingMatch
from wrestling_tracker.storage import JsonMatchRepository
from wrestling_tracker.tracker import SeasonTracker


@pytest.fixture(autouse=True)
def protect_real_data_file(tmp_path, monkeypatch):
    """Point the CLI's default data file at a temporary path for every test.

    Tests normally pass their own repository, but if one forgets, this makes
    sure the real data/matches.json is still never read or written.
    """
    monkeypatch.setattr(cli, "DEFAULT_DATA_FILE", tmp_path / "default.json")


@pytest.fixture
def winning_match():
    """Return a match the wrestler won, 8-4 against John Smith."""
    return WrestlingMatch("John Smith", 8, 4)


@pytest.fixture
def losing_match():
    """Return a match the wrestler lost, 3-5 against Mike Davis."""
    return WrestlingMatch("Mike Davis", 3, 5)


@pytest.fixture
def season_tracker(winning_match, losing_match):
    """Return a tracker holding one win (8-4) and one loss (3-5)."""
    return SeasonTracker([winning_match, losing_match])


@pytest.fixture
def repository(tmp_path):
    """Return a JsonMatchRepository that writes inside a temporary folder."""
    return JsonMatchRepository(tmp_path / "data" / "matches.json")
