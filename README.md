[YouTube Presentation](https://youtu.be/SLg932WUy7A)

# Wrestling Match Tracker

**Author:** Aayush Pande
**Course project:** CSCI-1511 Project 2 (Option A: refactor an existing project)

## Overview

Wrestling Match Tracker is a command-line program for recording wrestling
matches and viewing statistics about a season. You enter each match (opponent
name plus both scores), the program works out whether it was a win or a loss,
and everything is saved to a JSON file so your season is still there the next
time you start the program.

This is the Project 2 refactor of my Project 1 program. Project 1 was one
script that kept matches in a list of dictionaries and lost them when it
exited. Project 2 keeps every Project 1 feature and rebuilds the program with
functions, multiple modules, classes, inheritance, file input/output,
exception handling, JSON persistence, and automated tests (Chapters 8-11 of
*Python Crash Course*).

## Features

- **Add Match** - enter an opponent name, your score, and the opponent's
  score. The program records a win or loss and saves it immediately.
- **View Matches** - a numbered history such as `1. John Smith - WIN 8-4`.
- **View Season Statistics** - total matches, wins, losses, win percentage,
  total points scored, and average points per match.
- **Search Opponent** - find matches by opponent name. The search ignores
  capitalization and accepts part of a name (`mike` finds `Mike Davis`).
- **Exit** - ends the program cleanly.
- **Validation** - empty names, non-numeric scores, negative scores, and tied
  scores (wrestling matches always have a winner) are rejected with a clear
  message and nothing is saved.
- **Persistence** - matches are stored in `data/matches.json` and loaded again
  at startup.
- **Safe error handling** - a damaged data file produces an explanation instead
  of a traceback and is never overwritten. Ctrl+C and Ctrl+D also exit
  without a traceback.

## Installation

You need Python 3 (developed and tested with Python 3.13). The program itself
uses only the standard library. The only third-party package is `pytest`, used
for the tests.

```bash
# Optional: use a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Only needed to run the tests
python3 -m pip install -r requirements.txt
```

## How to Run

From the project folder (the one containing `wrestling_match_tracker.py`):

```bash
python3 wrestling_match_tracker.py
```

(On Windows you may need `python` instead of `python3`.) Type a number from 1
to 5 at the menu and press Enter.

### How to Run the Tests

```bash
python3 -m pytest -v
```

The tests only use temporary folders, so they never read or change your real
`data/matches.json`. To also check that every file compiles:

```bash
python3 -m compileall wrestling_match_tracker.py wrestling_tracker tests
```

## Manual Happy-Path Demonstration

This is the walkthrough I use to check the whole program. Start with no
`data/matches.json` (delete it if it exists). Typed input follows each prompt.

**Run 1 - add a win and a loss, then look at the results**

```text
WRESTLING MATCH TRACKER

1. Add Match
2. View Matches
3. View Season Statistics
4. Search Opponent
5. Exit
Choose an option (1-5): 1
Opponent name: John Smith
Your score: 8
Opponent score: 4

Match recorded: WIN 8-4
```

Add a second match the same way (`Mike Davis`, `3`, `5` gives
`Match recorded: LOSS 3-5`). Then option 2, option 3, and option 4 (searching
for `mike`) show:

```text
MATCH HISTORY
1. John Smith - WIN 8-4
2. Mike Davis - LOSS 3-5

SEASON STATISTICS

Matches: 2
Wins: 1
Losses: 1
Win Percentage: 50.0%
Points Scored: 11
Average Points: 5.5

MATCHES FOR 'mike'
2. Mike Davis - LOSS 3-5
```

Choose option 5 to exit (`Goodbye!`).

**Run 2 - restart the program and confirm the matches persisted**

```text
WRESTLING MATCH TRACKER
Loaded 2 saved matches.
```

Option 2 shows the same two matches, so nothing was lost between runs.

## How Persistence Works

1. At startup the program asks `JsonMatchRepository.load()` for the saved
   matches and gives them to a new `SeasonTracker`.
2. Every time a valid match is added, the whole season is saved straight away
   with `JsonMatchRepository.save()`. Rejected input and ties are never saved.
3. If the program stops unexpectedly, every match added before that point is
   already on disk.

### JSON Storage Behavior

The file is `data/matches.json`:

```json
{
  "format_version": 1,
  "matches": [
    {
      "opponent_name": "John Smith",
      "wrestler_score": 8,
      "opponent_score": 4
    },
    {
      "opponent_name": "Mike Davis",
      "wrestler_score": 3,
      "opponent_score": 5
    }
  ]
}
```

- **The result is not stored.** Win or Loss is calculated from the two scores
  when a match is loaded, so the file can never disagree with itself.
- **`format_version`** lets the program recognize a file layout it does not
  understand instead of misreading it.
- **A missing file is normal.** It means nothing has been saved yet, so the
  season starts empty. Loading never creates the file.
- **The folder is created if needed** when saving.
- **Saves are atomic.** Data is written to a temporary file and then moved into
  place, so a crash in the middle of a save cannot leave a half-written data
  file.
- **The data file is ignored by Git** (see `.gitignore`), so personal or demo
  data is not committed. `data/.gitkeep` keeps the folder in the repository.

## Error-Handling Behavior

| Situation | What the program does |
|---|---|
| Empty name, non-numeric score, negative score | Explains the problem and asks again. |
| Tied scores | Prints "Matches cannot end in a tie. Match not recorded." Nothing is saved. |
| Data file is not valid JSON, has the wrong layout or version, or contains an invalid match | Prints `Could not load saved matches.` with the reason, exits with status 1, and **leaves the file untouched** so it can be repaired. |
| Data file cannot be read (for example, it is a folder or has the wrong encoding) | Same message and exit status 1. |
| Saving fails (full disk, no permission) | Prints a warning; the match stays in memory for the rest of the session, and the program keeps running. |
| Ctrl+D (closed input) | Prints `Input closed. Goodbye!` and exits normally (status 0). |
| Ctrl+C | Prints `Interrupted. Goodbye!` and exits with status 130. Matches already added are already saved. |

The program never deletes, renames, or silently replaces a data file it
cannot read. Example of a damaged file:

```text
WRESTLING MATCH TRACKER

Could not load saved matches. .../data/matches.json is not valid JSON (Expecting property name enclosed in double quotes: line 1 column 2 (char 1)). The file was left untouched so you can repair it.
Fix or move the file, then start the program again.
```

## Project Structure

```text
.
├── wrestling_match_tracker.py   # small entry point: python3 wrestling_match_tracker.py
├── wrestling_tracker/           # the application package
│   ├── __init__.py
│   ├── match.py                 # WrestlingMatch and the validation rules
│   ├── tracker.py               # SeasonTracker: history, search, statistics
│   ├── storage.py               # MatchRepository and JsonMatchRepository
│   ├── exceptions.py            # MatchValidationError, DataPersistenceError
│   └── cli.py                   # all input and printing, and the menu loop
├── tests/                       # pytest test suite
│   ├── __init__.py
│   ├── conftest.py              # shared fixtures and real-data protection
│   ├── test_match.py
│   ├── test_tracker.py
│   ├── test_storage.py
│   └── test_cli.py
├── data/
│   └── .gitkeep                 # keeps the folder; matches.json is created at run time
├── requirements.txt             # pytest
├── .gitignore
└── README.md
```

## Architecture and Justification

Each module has one job, and the dependencies only point one way
(`cli` -> `tracker`/`storage` -> `match` -> `exceptions`):

- **`WrestlingMatch`** (`match.py`) represents one completed match. It
  validates its own data when it is created, rejects ties, and calculates the
  result from the scores. Its fields are read-only, so a match can never become
  invalid after it is created. `to_dict()` and `from_dict()` convert it to and
  from plain dictionaries for JSON.
- **`SeasonTracker`** (`tracker.py`) owns the list of matches and answers
  questions about them: history, case-insensitive partial search, and
  statistics. It returns data and never prints.
- **`MatchRepository` / `JsonMatchRepository`** (`storage.py`) handle saving
  and loading. The base class only declares `load()` and `save()`.
- **`cli.py`** handles input and printing only. It does not calculate
  anything: rules live in `WrestlingMatch`, calculations in `SeasonTracker`,
  and file access in the repository.

### Why `SeasonTracker` uses composition

A season tracker *has* matches; it is not a kind of match. Making it inherit
from `WrestlingMatch` would be wrong because it would claim a season is a
single match with an opponent and two scores. Instead, `SeasonTracker` holds a
list of `WrestlingMatch` objects (composition), which is what the "has-a"
relationship calls for. It also hands out copies of that list so other code
cannot change it by accident.

### Why inheritance is used for storage

`JsonMatchRepository` *is a* `MatchRepository`: it is one specific way to do
the general job "load and save a season". The CLI is written against the
`MatchRepository` interface, so a different storage format could be dropped in
without changing the CLI. The tests use this too: one CLI test uses a small
`MatchRepository` subclass whose `save()` always fails, to check the warning
path. I deliberately kept the hierarchy to this one relationship instead of
building a deep or artificial one.

## Chapters 8-11 Competency Mapping

| Chapter | Concept | Where it appears |
|---|---|---|
| **8 - Functions** | Defining functions, parameters, arguments, return values | `cli.py` (`prompt_for_score(prompt)`, `format_match(match_number, match)`, `add_match(tracker, repository)`); `validate_score()` and `validate_opponent_name()` return the cleaned value. |
| | Default values and keyword arguments | `SeasonTracker(matches=None)`, `main(repository=None)`, and `enumerate(..., start=1)`. |
| | Storing functions in modules and importing them | The code is split into five modules in the `wrestling_tracker` package and imported with `from ... import ...`. |
| **9 - Classes** | Classes, attributes, methods, `__init__` | `WrestlingMatch`, `SeasonTracker`, `MatchRepository`, `JsonMatchRepository`. |
| | Inheritance | `JsonMatchRepository(MatchRepository)`; `MatchValidationError` and `DataPersistenceError` also subclass built-in exceptions. |
| | Instances as attributes / composition | `SeasonTracker` holds `WrestlingMatch` objects. |
| | Importing classes and the standard library | `json`, `pathlib.Path`, and `abc`. |
| **10 - Files and exceptions** | Reading and writing files with `pathlib` | `Path.read_text()`, `Path.open()`, `Path.mkdir()`, and `Path.replace()` in `storage.py`. |
| | Storing data with `json` | Reading with `json.loads()` and writing with `json.dump()`. |
| | `try` / `except` | `FileNotFoundError`, `OSError`, `UnicodeDecodeError`, `json.JSONDecodeError`, `KeyError`, and the project's own exceptions are each caught specifically; there is no bare `except`. |
| | Raising exceptions and custom exceptions | `MatchValidationError`, `DataPersistenceError`, and `raise ... from error` to keep the original cause. |
| **11 - Testing** | Testing functions and classes with `pytest` | `tests/` has four test files and a `conftest.py`. |
| | Fixtures | `winning_match`, `losing_match`, `season_tracker`, and `repository` in `conftest.py`. |
| | Many cases with one test | `@pytest.mark.parametrize` for invalid names, scores, and records. |
| | Temporary files | `tmp_path` for all storage tests. |
| | Checking printed output | `capsys` and `monkeypatch` (to supply scripted input) in `test_cli.py`. |

### Concepts used that go slightly beyond the chapters

- `@property` and `@classmethod` (`WrestlingMatch`) and `abc.ABC` /
  `@abstractmethod` (`MatchRepository`). The properties make the fields
  read-only, the class method builds a match from a dictionary, and the
  abstract base class makes Python refuse to create a repository that forgot to
  implement `load()` or `save()`.
- `pytest` fixtures and `parametrize` are written as decorators.

## Testing

Run `python3 -m pytest -v`. The suite has 179 tests:

| File | Focus |
|---|---|
| `test_match.py` | Win/loss calculation; rejection of empty names, booleans, non-integer scores, negative scores, and ties; read-only fields; `to_dict()`/`from_dict()` round trip; malformed records. |
| `test_tracker.py` | History and composition; statistics for empty, known, and changing seasons; case-insensitive partial search. |
| `test_storage.py` | Missing file, save/load round trip, folder creation, malformed JSON, invalid stored matches, and filesystem failures. |
| `test_cli.py` | Adding with immediate save, retry on bad input, ties not saved, history/statistics/search output, persistence across runs, damaged data, and Ctrl+C/Ctrl+D. |

The CLI tests check outcomes (what is saved, exit status, key messages) rather
than exact formatting, so they do not break when wording is polished.

## Project Development

**Project 1** was built phase by phase as a single script (menu, match
recording, validation, history, statistics, search, refactoring into
functions, testing, and documentation). Its history is preserved unchanged in
this repository.
