"""
Wrestling Match Tracker
Author: Aayush Pande
Purpose: Tests for the command-line interface. They feed scripted input to
    main() and check the important outcomes (what is saved, exit status, and
    key messages) rather than exact formatting, so cosmetic changes do not
    break them. All storage is temporary.
Starter Code/Resources: None
Date: 2026-11-04
"""

import pytest

from wrestling_tracker import cli
from wrestling_tracker.exceptions import DataPersistenceError
from wrestling_tracker.match import WrestlingMatch
from wrestling_tracker.storage import MatchRepository


def run_cli(monkeypatch, capsys, repository, *typed_lines):
    """Run main() with scripted keyboard input.

    When the script runs out, input() raises EOFError just like a closed
    terminal would.

    Args:
        monkeypatch: pytest's monkeypatch fixture.
        capsys: pytest's capture fixture.
        repository: The repository main() should use.
        *typed_lines: The lines the "user" types, in order.

    Returns:
        A (exit_status, printed_output) tuple.
    """
    remaining_lines = iter(typed_lines)

    def fake_input(prompt=""):
        """Print the prompt like input() and return the next scripted line."""
        print(prompt, end="")
        try:
            return next(remaining_lines)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr("builtins.input", fake_input)
    exit_status = cli.main(repository)
    return exit_status, capsys.readouterr().out


def stored_names(repository):
    """Return the opponent names currently saved in the repository."""
    return [match.opponent_name for match in repository.load()]


class FailingSaveRepository(MatchRepository):
    """Repository whose save() always fails, to test the warning path."""

    def load(self):
        """Return an empty season."""
        return []

    def save(self, matches):
        """Always fail like a full disk would."""
        raise DataPersistenceError("disk is full")


class TestAddMatch:
    """Adding matches records them and saves immediately."""

    def test_valid_match_is_recorded_and_saved(
        self, monkeypatch, capsys, repository
    ):
        """A win is reported and written to storage straight away."""
        status, output = run_cli(
            monkeypatch, capsys, repository, "1", "John Smith", "8", "4", "5"
        )
        assert status == 0
        assert "Match recorded: WIN 8-4" in output
        assert repository.load() == [WrestlingMatch("John Smith", 8, 4)]

    def test_loss_is_recorded(self, monkeypatch, capsys, repository):
        """A lower score is reported as a loss."""
        _, output = run_cli(
            monkeypatch, capsys, repository, "1", "Mike Davis", "3", "5", "5"
        )
        assert "Match recorded: LOSS 3-5" in output
        assert repository.load()[0].result == "Loss"

    def test_match_is_saved_even_if_the_user_never_exits(
        self, monkeypatch, capsys, repository
    ):
        """Saving happens right after adding, not at exit."""
        run_cli(monkeypatch, capsys, repository, "1", "A", "2", "1")
        assert stored_names(repository) == ["A"]

    def test_tie_is_rejected_and_not_saved(
        self, monkeypatch, capsys, repository
    ):
        """Tied scores are refused and nothing is written."""
        _, output = run_cli(
            monkeypatch, capsys, repository, "1", "Tie Guy", "5", "5", "5"
        )
        assert "tie" in output.lower()
        assert not repository.file_path.exists()

    def test_invalid_input_is_asked_again(
        self, monkeypatch, capsys, repository
    ):
        """Bad names and scores re-prompt until the input is valid."""
        _, output = run_cli(
            monkeypatch, capsys, repository,
            "1",
            "", "   ", "John Smith",    # empty names, then a good one
            "abc", "-3", "3.5", "", "8",  # bad scores, then a good one
            "xyz", "-1", "4",
            "5",
        )
        assert "Opponent name cannot be empty." in output
        assert "Please enter a whole number." in output
        assert "Score cannot be negative." in output
        assert repository.load() == [WrestlingMatch("John Smith", 8, 4)]

    def test_unusual_digit_characters_do_not_crash(
        self, monkeypatch, capsys, repository
    ):
        """A superscript digit looks numeric but must be re-prompted."""
        _, output = run_cli(
            monkeypatch, capsys, repository, "1", "A", "²", "3", "1", "5"
        )
        assert "Please enter a whole number." in output
        assert repository.load() == [WrestlingMatch("A", 3, 1)]

    def test_failed_save_warns_but_keeps_the_match_in_memory(
        self, monkeypatch, capsys
    ):
        """A save failure shows a warning, not a traceback, and the session
        continues with the match still viewable."""
        status, output = run_cli(
            monkeypatch, capsys, FailingSaveRepository(),
            "1", "A", "2", "1", "2", "5",
        )
        assert status == 0
        assert "could not be saved" in output
        assert "disk is full" in output
        assert "1. A - WIN 2-1" in output


class TestViewing:
    """History, statistics, and search display the right information."""

    def test_empty_history_message(self, monkeypatch, capsys, repository):
        """With no matches the user is told so."""
        _, output = run_cli(monkeypatch, capsys, repository, "2", "5")
        assert "No matches recorded yet." in output

    def test_history_lists_matches_in_order(
        self, monkeypatch, capsys, repository
    ):
        """The history is numbered and shows result and score."""
        _, output = run_cli(
            monkeypatch, capsys, repository,
            "1", "John Smith", "8", "4",
            "1", "Mike Davis", "3", "5",
            "2", "5",
        )
        assert "1. John Smith - WIN 8-4" in output
        assert "2. Mike Davis - LOSS 3-5" in output
        assert output.index("1. John Smith - WIN") < output.index(
            "2. Mike Davis - LOSS"
        )

    def test_empty_statistics_message(self, monkeypatch, capsys, repository):
        """Statistics with no matches say so instead of showing zeros."""
        _, output = run_cli(monkeypatch, capsys, repository, "3", "5")
        assert "No matches recorded yet." in output

    def test_statistics_for_a_known_season(
        self, monkeypatch, capsys, repository
    ):
        """Three known matches give 2-1, 66.7%, 21 points, 7.0 average."""
        _, output = run_cli(
            monkeypatch, capsys, repository,
            "1", "John Smith", "8", "4",
            "1", "Mike Davis", "3", "5",
            "1", "Alex Brown", "10", "2",
            "3", "5",
        )
        assert "Matches: 3" in output
        assert "Wins: 2" in output
        assert "Losses: 1" in output
        assert "Win Percentage: 66.7%" in output
        assert "Points Scored: 21" in output
        assert "Average Points: 7.0" in output

    def test_search_is_case_insensitive_and_partial(
        self, monkeypatch, capsys, repository
    ):
        """A lowercase fragment finds the opponent with its history number."""
        _, output = run_cli(
            monkeypatch, capsys, repository,
            "1", "John Smith", "8", "4",
            "1", "Mike Davis", "3", "5",
            "4", "mike", "5",
        )
        assert "2. Mike Davis - LOSS 3-5" in output
        assert output.rsplit("MATCHES FOR", 1)[1].count("John Smith") == 0

    def test_search_with_no_result(self, monkeypatch, capsys, repository):
        """An unknown name gets a clear message."""
        _, output = run_cli(
            monkeypatch, capsys, repository,
            "1", "John Smith", "8", "4", "4", "Zed", "5",
        )
        assert "No matches found for 'Zed'." in output

    def test_blank_search_is_refused(self, monkeypatch, capsys, repository):
        """A blank search name is rejected without searching."""
        _, output = run_cli(monkeypatch, capsys, repository, "4", "   ", "5")
        assert "Search name cannot be empty." in output


class TestMenu:
    """Menu navigation and exiting."""

    def test_exit_returns_zero_and_says_goodbye(
        self, monkeypatch, capsys, repository
    ):
        """Choosing 5 ends the program normally."""
        status, output = run_cli(monkeypatch, capsys, repository, "5")
        assert status == 0
        assert "Goodbye!" in output

    @pytest.mark.parametrize("bad_choice", ["", "0", "6", "abc", "1.0", "-1"])
    def test_invalid_menu_choice_shows_menu_again(
        self, monkeypatch, capsys, repository, bad_choice
    ):
        """Anything other than 1-5 is refused and the loop continues."""
        status, output = run_cli(
            monkeypatch, capsys, repository, bad_choice, "5"
        )
        assert status == 0
        assert "Invalid choice" in output
        assert "Goodbye!" in output

    def test_menu_choice_tolerates_spaces(
        self, monkeypatch, capsys, repository
    ):
        """" 5 " is treated as 5."""
        _, output = run_cli(monkeypatch, capsys, repository, " 5 ")
        assert "Goodbye!" in output


class TestPersistenceAcrossRuns:
    """Matches survive restarting the program."""

    def test_matches_are_loaded_on_the_next_run(
        self, monkeypatch, capsys, repository
    ):
        """A second run sees the first run's matches."""
        run_cli(
            monkeypatch, capsys, repository,
            "1", "John Smith", "8", "4", "1", "Mike Davis", "3", "5", "5",
        )
        status, output = run_cli(monkeypatch, capsys, repository, "2", "5")
        assert status == 0
        assert "Loaded 2 saved matches." in output
        assert "1. John Smith - WIN 8-4" in output
        assert "2. Mike Davis - LOSS 3-5" in output

    def test_new_matches_are_added_after_loaded_ones(
        self, monkeypatch, capsys, repository
    ):
        """A restarted session appends instead of overwriting."""
        run_cli(monkeypatch, capsys, repository, "1", "First", "2", "1", "5")
        run_cli(monkeypatch, capsys, repository, "1", "Second", "3", "1", "5")
        assert stored_names(repository) == ["First", "Second"]

    def test_default_repository_uses_the_default_data_file(
        self, monkeypatch, capsys, tmp_path
    ):
        """main() with no repository uses cli.DEFAULT_DATA_FILE (which the
        autouse fixture points at a temporary path)."""
        run_cli(monkeypatch, capsys, None, "1", "A", "2", "1", "5")
        assert cli.DEFAULT_DATA_FILE.parent == tmp_path
        assert cli.DEFAULT_DATA_FILE.is_file()

    def test_real_data_file_is_never_used_by_tests(self):
        """The protection fixture really redirects the default path."""
        assert cli.DEFAULT_DATA_FILE.name == "default.json"


class TestDamagedData:
    """A damaged data file stops the program without touching the file."""

    @pytest.mark.parametrize(
        "damaged_text",
        [
            "{not json",
            "",
            '{"format_version": 1, "matches": [{"opponent_name": "A"}]}',
            '{"format_version": 1, "matches": "nope"}',
        ],
    )
    def test_damaged_file_exits_with_status_one_and_is_preserved(
        self, monkeypatch, capsys, repository, damaged_text
    ):
        """The user gets an explanation and the file is left as it was."""
        repository.file_path.parent.mkdir(parents=True)
        repository.file_path.write_text(damaged_text, encoding="utf-8")

        status, output = run_cli(
            monkeypatch, capsys, repository, "1", "New", "9", "1", "5"
        )

        assert status == 1
        assert "Could not load saved matches." in output
        assert "Traceback" not in output
        assert repository.file_path.read_text(encoding="utf-8") == damaged_text

    def test_menu_is_never_shown_for_damaged_data(
        self, monkeypatch, capsys, repository
    ):
        """Without valid data the program does not let the user add matches
        that would overwrite the damaged file."""
        repository.file_path.parent.mkdir(parents=True)
        repository.file_path.write_text("{bad", encoding="utf-8")
        _, output = run_cli(monkeypatch, capsys, repository, "5")
        assert "1. Add Match" not in output


class TestInterruptions:
    """Ctrl+D and Ctrl+C end the program without a traceback."""

    def test_closed_input_exits_cleanly(
        self, monkeypatch, capsys, repository
    ):
        """EOFError at the menu is a normal exit."""
        status, output = run_cli(monkeypatch, capsys, repository)
        assert status == 0
        assert "Goodbye!" in output

    def test_closed_input_in_the_middle_of_add_match_saves_nothing(
        self, monkeypatch, capsys, repository
    ):
        """An unfinished match is discarded, not half saved."""
        status, _ = run_cli(monkeypatch, capsys, repository, "1", "A", "2")
        assert status == 0
        assert not repository.file_path.exists()

    def test_keyboard_interrupt_exits_with_130(
        self, monkeypatch, capsys, repository
    ):
        """Ctrl+C returns the conventional interrupted status."""

        def interrupted_input(prompt=""):
            """Simulate the user pressing Ctrl+C."""
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", interrupted_input)
        status = cli.main(repository)
        output = capsys.readouterr().out
        assert status == 130
        assert "Interrupted" in output

    def test_interrupt_keeps_matches_saved_earlier(
        self, monkeypatch, capsys, repository
    ):
        """Matches added before the interruption are still in the file."""
        run_cli(monkeypatch, capsys, repository, "1", "Saved", "4", "1")

        def interrupted_input(prompt=""):
            """Simulate the user pressing Ctrl+C."""
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", interrupted_input)
        cli.main(repository)
        assert stored_names(repository) == ["Saved"]


class TestEntryPoint:
    """The original command still works through the guarded entry point."""

    def test_entry_point_exposes_main(self):
        """wrestling_match_tracker re-exports the CLI's main()."""
        import wrestling_match_tracker

        assert wrestling_match_tracker.main is cli.main

    def test_importing_the_entry_point_does_not_start_the_program(self):
        """The __main__ guard keeps imports side-effect free (no prompt)."""
        import wrestling_match_tracker  # would raise EOFError if it ran

        assert callable(wrestling_match_tracker.main)
