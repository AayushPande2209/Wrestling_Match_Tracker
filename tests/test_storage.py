"""
Wrestling Match Tracker
Author: Aayush Pande
Purpose: Tests for MatchRepository and JsonMatchRepository: loading, saving,
    missing files, malformed data, and persistence failures. Every test uses
    pytest's tmp_path, never the real data/matches.json.
Starter Code/Resources: None
Date: 2026-11-04
"""

import json
from pathlib import Path

import pytest

from wrestling_tracker.exceptions import DataPersistenceError
from wrestling_tracker.match import WrestlingMatch
from wrestling_tracker.storage import (
    FORMAT_VERSION,
    JsonMatchRepository,
    MatchRepository,
)

VALID_RECORD = {
    "opponent_name": "John Smith",
    "wrestler_score": 8,
    "opponent_score": 4,
}


def write_json_file(file_path, stored_data):
    """Write stored_data to file_path as JSON, creating folders as needed."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(stored_data), encoding="utf-8")


class TestInheritance:
    """JsonMatchRepository is one implementation of the storage interface."""

    def test_json_repository_is_a_match_repository(self, repository):
        """The CLI can treat it as any MatchRepository."""
        assert isinstance(repository, MatchRepository)

    def test_interface_cannot_be_instantiated(self):
        """The abstract base class has no storage behavior of its own."""
        with pytest.raises(TypeError):
            MatchRepository()

    def test_subclass_must_implement_both_operations(self):
        """A subclass that only defines load() is still abstract."""

        class LoadOnlyRepository(MatchRepository):
            """Incomplete repository proving the interface is enforced."""

            def load(self):
                """Return no matches."""
                return []

        with pytest.raises(TypeError):
            LoadOnlyRepository()

    def test_accepts_string_paths(self, tmp_path):
        """A plain string is converted to a Path."""
        repository = JsonMatchRepository(str(tmp_path / "m.json"))
        assert isinstance(repository.file_path, Path)


class TestLoading:
    """load() turns stored JSON back into WrestlingMatch objects."""

    def test_missing_file_is_an_empty_season(self, repository):
        """No file means nothing saved yet, which is not an error."""
        assert repository.load() == []

    def test_loading_a_missing_file_does_not_create_it(self, repository):
        """Reading must have no side effects on the filesystem."""
        repository.load()
        assert not repository.file_path.exists()
        assert not repository.file_path.parent.exists()

    def test_loads_valid_records_as_matches(self, repository):
        """Stored dictionaries become WrestlingMatch objects."""
        write_json_file(
            repository.file_path,
            {"format_version": FORMAT_VERSION, "matches": [VALID_RECORD]},
        )
        loaded_matches = repository.load()
        assert loaded_matches == [WrestlingMatch("John Smith", 8, 4)]
        assert loaded_matches[0].result == "Win"

    def test_empty_matches_list_is_valid(self, repository):
        """A file with no matches loads as an empty season."""
        write_json_file(
            repository.file_path,
            {"format_version": FORMAT_VERSION, "matches": []},
        )
        assert repository.load() == []

    def test_load_preserves_match_order(self, repository):
        """Matches come back in the order they were stored."""
        names = ["A", "B", "C"]
        write_json_file(
            repository.file_path,
            {
                "format_version": FORMAT_VERSION,
                "matches": [
                    {"opponent_name": name, "wrestler_score": 2,
                     "opponent_score": 1}
                    for name in names
                ],
            },
        )
        loaded_names = [match.opponent_name for match in repository.load()]
        assert loaded_names == names


class TestSaving:
    """save() writes readable JSON and creates missing folders."""

    def test_save_creates_missing_parent_directories(self, tmp_path):
        """A deep folder that does not exist yet is created on save."""
        file_path = tmp_path / "one" / "two" / "matches.json"
        JsonMatchRepository(file_path).save([WrestlingMatch("A", 2, 1)])
        assert file_path.is_file()

    def test_save_load_round_trip(
        self, repository, winning_match, losing_match
    ):
        """What is saved is exactly what is loaded."""
        repository.save([winning_match, losing_match])
        assert repository.load() == [winning_match, losing_match]

    def test_round_trip_restores_results(self, repository, losing_match):
        """The derived result is recalculated correctly after loading."""
        repository.save([losing_match])
        assert repository.load()[0].result == "Loss"

    def test_saved_file_has_a_stable_readable_layout(
        self, repository, winning_match
    ):
        """The JSON has a format version and a list of plain records."""
        repository.save([winning_match])
        stored_text = repository.file_path.read_text(encoding="utf-8")
        assert json.loads(stored_text) == {
            "format_version": FORMAT_VERSION,
            "matches": [VALID_RECORD],
        }

    def test_result_is_not_duplicated_in_the_file(
        self, repository, winning_match
    ):
        """Derived data stays out of storage."""
        repository.save([winning_match])
        assert "result" not in repository.file_path.read_text(encoding="utf-8")

    def test_save_replaces_previous_contents(
        self, repository, winning_match, losing_match
    ):
        """Saving a shorter season does not keep old matches."""
        repository.save([winning_match, losing_match])
        repository.save([losing_match])
        assert repository.load() == [losing_match]

    def test_saving_nothing_writes_a_valid_empty_season(self, repository):
        """An empty save can be loaded again."""
        repository.save([])
        assert repository.load() == []

    def test_save_accepts_any_iterable(self, repository, winning_match):
        """A generator works as well as a list."""
        repository.save(match for match in [winning_match])
        assert repository.load() == [winning_match]

    def test_non_ascii_names_survive_a_round_trip(self, repository):
        """Accented names are stored and read back unchanged."""
        match = WrestlingMatch("José Muñoz", 3, 1)
        repository.save([match])
        assert repository.load() == [match]

    def test_no_temporary_file_is_left_behind(
        self, repository, winning_match
    ):
        """The temporary file used for safe writing is cleaned up."""
        repository.save([winning_match])
        leftovers = [
            path.name for path in repository.file_path.parent.iterdir()
            if path.name != repository.file_path.name
        ]
        assert leftovers == []


class TestMalformedData:
    """Bad files raise DataPersistenceError and are never modified."""

    @pytest.mark.parametrize(
        "bad_text",
        [
            "",                    # empty file
            "{not json",           # syntax error
            '{"format_version": 1, "matches": [',  # truncated
            "null nonsense",
        ],
    )
    def test_invalid_json_raises(self, repository, bad_text):
        """Text that is not JSON is reported, not crashed on."""
        repository.file_path.parent.mkdir(parents=True)
        repository.file_path.write_text(bad_text, encoding="utf-8")
        with pytest.raises(DataPersistenceError, match="not valid JSON"):
            repository.load()

    def test_json_error_is_kept_as_the_cause(self, repository):
        """The original JSONDecodeError is chained for debugging."""
        repository.file_path.parent.mkdir(parents=True)
        repository.file_path.write_text("{bad", encoding="utf-8")
        with pytest.raises(DataPersistenceError) as error_info:
            repository.load()
        assert isinstance(error_info.value.__cause__, json.JSONDecodeError)

    def test_malformed_file_is_left_untouched(self, repository):
        """Loading a damaged file must never alter or delete it."""
        repository.file_path.parent.mkdir(parents=True)
        repository.file_path.write_text("{bad", encoding="utf-8")
        with pytest.raises(DataPersistenceError):
            repository.load()
        assert repository.file_path.read_text(encoding="utf-8") == "{bad"

    def test_non_utf8_bytes_raise(self, repository):
        """Binary garbage is a persistence error, not a UnicodeDecodeError."""
        repository.file_path.parent.mkdir(parents=True)
        repository.file_path.write_bytes(b"\xff\xfe\x00bad")
        with pytest.raises(DataPersistenceError, match="Could not read"):
            repository.load()

    @pytest.mark.parametrize(
        "stored_data",
        [
            [],
            [VALID_RECORD],
            "text",
            5,
            None,
        ],
    )
    def test_top_level_must_be_an_object(self, repository, stored_data):
        """Only a JSON object is a valid season file."""
        write_json_file(repository.file_path, stored_data)
        with pytest.raises(DataPersistenceError, match="JSON object"):
            repository.load()

    @pytest.mark.parametrize("version", [None, 0, 2, "1"])
    def test_unsupported_format_version_raises(self, repository, version):
        """A missing or different version is refused, not guessed at."""
        write_json_file(
            repository.file_path, {"format_version": version, "matches": []}
        )
        with pytest.raises(DataPersistenceError, match="format_version"):
            repository.load()

    def test_missing_version_key_raises(self, repository):
        """A file without a format_version is unsupported."""
        write_json_file(repository.file_path, {"matches": []})
        with pytest.raises(DataPersistenceError, match="format_version"):
            repository.load()

    @pytest.mark.parametrize("matches_value", ["nope", {}, 5, None])
    def test_matches_must_be_a_list(self, repository, matches_value):
        """The "matches" entry must be a list."""
        write_json_file(
            repository.file_path,
            {"format_version": FORMAT_VERSION, "matches": matches_value},
        )
        with pytest.raises(DataPersistenceError, match="list named 'matches'"):
            repository.load()

    def test_missing_matches_key_raises(self, repository):
        """A file without a "matches" entry is invalid."""
        write_json_file(
            repository.file_path, {"format_version": FORMAT_VERSION}
        )
        with pytest.raises(DataPersistenceError, match="'matches'"):
            repository.load()

    @pytest.mark.parametrize(
        "bad_record",
        [
            {"opponent_name": "A", "wrestler_score": 3, "opponent_score": 3},
            {"opponent_name": "A", "wrestler_score": -1, "opponent_score": 3},
            {"opponent_name": "A", "wrestler_score": "3",
             "opponent_score": 1},
            {"opponent_name": "A", "wrestler_score": 2.5,
             "opponent_score": 1},
            {"opponent_name": "A", "wrestler_score": True,
             "opponent_score": 0},
            {"opponent_name": "   ", "wrestler_score": 3,
             "opponent_score": 1},
            {"opponent_name": "A", "wrestler_score": 3},
            {},
            "not a dictionary",
            None,
            42,
        ],
    )
    def test_invalid_stored_match_raises(self, repository, bad_record):
        """A stored record that is not a valid match fails the load."""
        write_json_file(
            repository.file_path,
            {"format_version": FORMAT_VERSION, "matches": [bad_record]},
        )
        with pytest.raises(DataPersistenceError, match="Match record 1"):
            repository.load()

    def test_error_names_the_position_of_the_bad_record(self, repository):
        """With several records, the message says which one is invalid."""
        write_json_file(
            repository.file_path,
            {
                "format_version": FORMAT_VERSION,
                "matches": [
                    VALID_RECORD,
                    VALID_RECORD,
                    {"opponent_name": "A", "wrestler_score": 1,
                     "opponent_score": 1},
                ],
            },
        )
        with pytest.raises(DataPersistenceError, match="Match record 3"):
            repository.load()

    def test_one_bad_record_does_not_load_a_partial_season(self, repository):
        """Data is never silently dropped: the whole load fails."""
        write_json_file(
            repository.file_path,
            {
                "format_version": FORMAT_VERSION,
                "matches": [VALID_RECORD, {"opponent_name": "A"}],
            },
        )
        with pytest.raises(DataPersistenceError):
            repository.load()

    def test_validation_error_is_kept_as_the_cause(self, repository):
        """The original MatchValidationError is chained."""
        write_json_file(
            repository.file_path,
            {"format_version": FORMAT_VERSION, "matches": [{}]},
        )
        with pytest.raises(DataPersistenceError) as error_info:
            repository.load()
        assert error_info.value.__cause__ is not None


class TestPersistenceFailures:
    """Filesystem problems become DataPersistenceError."""

    def test_load_when_path_is_a_directory_raises(self, tmp_path):
        """A directory sitting where the file should be is a read error."""
        file_path = tmp_path / "matches.json"
        file_path.mkdir()
        with pytest.raises(DataPersistenceError, match="Could not read"):
            JsonMatchRepository(file_path).load()

    def test_save_when_parent_is_a_file_raises(self, tmp_path, winning_match):
        """A parent "folder" that is really a file cannot be created."""
        blocking_file = tmp_path / "data"
        blocking_file.write_text("I am a file", encoding="utf-8")
        repository = JsonMatchRepository(blocking_file / "matches.json")
        with pytest.raises(DataPersistenceError, match="Could not save"):
            repository.save([winning_match])
        assert blocking_file.read_text(encoding="utf-8") == "I am a file"

    def test_os_error_is_kept_as_the_cause(self, tmp_path, winning_match):
        """The underlying OSError is chained for debugging."""
        blocking_file = tmp_path / "data"
        blocking_file.write_text("x", encoding="utf-8")
        repository = JsonMatchRepository(blocking_file / "matches.json")
        with pytest.raises(DataPersistenceError) as error_info:
            repository.save([winning_match])
        assert isinstance(error_info.value.__cause__, OSError)

    def test_failed_save_keeps_the_previous_file_and_cleans_up(
        self, repository, winning_match, losing_match, monkeypatch
    ):
        """If the final move fails, old data survives and no .tmp remains."""
        repository.save([winning_match])
        original_text = repository.file_path.read_text(encoding="utf-8")

        def failing_replace(self, target):
            """Simulate the operating system refusing to move the file."""
            raise OSError("simulated disk failure")

        monkeypatch.setattr(Path, "replace", failing_replace)
        with pytest.raises(DataPersistenceError, match="simulated disk"):
            repository.save([winning_match, losing_match])

        current_text = repository.file_path.read_text(encoding="utf-8")
        assert current_text == original_text
        assert list(repository.file_path.parent.glob("*.tmp")) == []
