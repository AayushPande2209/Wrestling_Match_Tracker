"""
Wrestling Match Tracker
Author: Aayush Pande
Purpose: Defines the storage interface (MatchRepository) and its JSON-file
    implementation (JsonMatchRepository) that keeps matches between runs.
Starter Code/Resources: None
Date: 2026-11-03
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path

from wrestling_tracker.exceptions import (
    DataPersistenceError,
    MatchValidationError,
)
from wrestling_tracker.match import WrestlingMatch

# Bump this if the JSON layout ever changes, so old files are detected
# instead of being misread.
FORMAT_VERSION = 1


class MatchRepository(ABC):
    """Interface for anything that can load and save a season of matches.

    The CLI depends on this interface rather than on a particular file
    format, so a different storage backend could replace JSON without
    changing the CLI. Subclasses must implement load() and save().
    """

    @abstractmethod
    def load(self):
        """Return the stored matches as a list of WrestlingMatch objects."""

    @abstractmethod
    def save(self, matches):
        """Store the given matches, replacing what was stored before.

        Args:
            matches: An iterable of WrestlingMatch objects.
        """


class JsonMatchRepository(MatchRepository):
    """Stores matches as a human-readable JSON file.

    The file looks like this::

        {
          "format_version": 1,
          "matches": [
            {"opponent_name": "John Smith",
             "wrestler_score": 8,
             "opponent_score": 4}
          ]
        }

    The result (Win or Loss) is not stored because it is derived from the
    scores when a match is loaded.
    """

    def __init__(self, file_path):
        """Remember where the JSON file lives; nothing is read yet.

        Args:
            file_path: A string or Path for the JSON file.
        """
        self._file_path = Path(file_path)

    @property
    def file_path(self):
        """Return the Path of the JSON file."""
        return self._file_path

    def load(self):
        """Read the JSON file and return its matches.

        A missing file is not an error: it means nothing has been saved yet,
        so an empty list is returned. The file is never modified or deleted.

        Returns:
            A list of WrestlingMatch objects (empty if the file is missing).

        Raises:
            DataPersistenceError: If the file cannot be read, is not valid
                JSON, has an unexpected layout, or contains an invalid match.
        """
        try:
            file_text = self._file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return []
        except (OSError, UnicodeDecodeError) as error:
            raise DataPersistenceError(
                f"Could not read {self._file_path}: {error}"
            ) from error

        try:
            stored_data = json.loads(file_text)
        except json.JSONDecodeError as error:
            raise DataPersistenceError(
                f"{self._file_path} is not valid JSON ({error}). "
                "The file was left untouched so you can repair it."
            ) from error

        return self._matches_from_stored_data(stored_data)

    def save(self, matches):
        """Write the matches to the JSON file, creating folders if needed.

        The data is written to a temporary file first and then moved into
        place, so a crash mid-write cannot leave a half-written data file.

        Args:
            matches: An iterable of WrestlingMatch objects.

        Raises:
            DataPersistenceError: If the file or its folder cannot be written.
        """
        stored_data = {
            "format_version": FORMAT_VERSION,
            "matches": [match.to_dict() for match in matches],
        }
        temporary_path = self._file_path.with_name(
            self._file_path.name + ".tmp"
        )
        try:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            with temporary_path.open("w", encoding="utf-8") as temporary_file:
                json.dump(stored_data, temporary_file, indent=2)
                temporary_file.write("\n")
            temporary_path.replace(self._file_path)
        except OSError as error:
            temporary_path.unlink(missing_ok=True)
            raise DataPersistenceError(
                f"Could not save to {self._file_path}: {error}"
            ) from error

    def _matches_from_stored_data(self, stored_data):
        """Turn parsed JSON into WrestlingMatch objects, checking its layout.

        Args:
            stored_data: The object produced by json.loads().

        Returns:
            A list of WrestlingMatch objects.

        Raises:
            DataPersistenceError: If the layout is wrong or any record is not
                a valid match. One bad record fails the whole load so data is
                never silently dropped.
        """
        if not isinstance(stored_data, dict):
            raise DataPersistenceError(
                f"{self._file_path} must contain a JSON object."
            )
        if stored_data.get("format_version") != FORMAT_VERSION:
            raise DataPersistenceError(
                f"{self._file_path} has an unsupported format_version."
            )
        stored_matches = stored_data.get("matches")
        if not isinstance(stored_matches, list):
            raise DataPersistenceError(
                f"{self._file_path} must contain a list named 'matches'."
            )

        matches = []
        for position, match_data in enumerate(stored_matches, start=1):
            try:
                matches.append(WrestlingMatch.from_dict(match_data))
            except MatchValidationError as error:
                raise DataPersistenceError(
                    f"Match record {position} in {self._file_path} "
                    f"is invalid: {error}"
                ) from error
        return matches
