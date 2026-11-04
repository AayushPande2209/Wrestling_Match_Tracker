"""
Wrestling Match Tracker
Author: Aayush Pande
Purpose: Command-line interface for the tracker. It owns all input and
    printing, and delegates match rules and calculations to WrestlingMatch
    and SeasonTracker, and storage to a MatchRepository.
Starter Code/Resources: Menu flow adapted from the Project 1 version of
    wrestling_match_tracker.py; no external resources.
Date: 2026-11-03
"""

from pathlib import Path

from wrestling_tracker.exceptions import (
    DataPersistenceError,
    MatchValidationError,
)
from wrestling_tracker.match import (
    WrestlingMatch,
    validate_opponent_name,
    validate_score,
)
from wrestling_tracker.storage import JsonMatchRepository
from wrestling_tracker.tracker import SeasonTracker

# Resolved from this file rather than the working directory so the program
# finds the same data folder no matter where it is started from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "matches.json"


def display_menu():
    """Print the main menu options."""
    print()
    print("1. Add Match")
    print("2. View Matches")
    print("3. View Season Statistics")
    print("4. Search Opponent")
    print("5. Exit")


def prompt_for_opponent_name():
    """Keep asking until the user enters a valid opponent name.

    Returns:
        The validated opponent name.
    """
    while True:
        try:
            return validate_opponent_name(input("Opponent name: "))
        except MatchValidationError as error:
            print(error)


def prompt_for_score(prompt):
    """Keep asking until the user enters a valid score.

    The text is checked here only to decide whether int() can convert it;
    the rules about what makes a score acceptable live in validate_score().

    Args:
        prompt: The text shown when asking for the score.

    Returns:
        The score as an int.
    """
    while True:
        score_text = input(prompt).strip()
        digits = score_text[1:] if score_text.startswith("-") else score_text
        # isdecimal() rather than isdigit(): isdigit() accepts characters such
        # as "²" that int() cannot convert.
        if not digits.isdecimal():
            print("Please enter a whole number.")
            continue
        try:
            return validate_score(int(score_text))
        except MatchValidationError as error:
            print(error)


def format_match(match_number, match):
    """Return one match as text, such as '1. John Smith - WIN 8-4'.

    Args:
        match_number: The match's position in the season, starting at 1.
        match: The WrestlingMatch to describe.
    """
    return (
        f"{match_number}. {match.opponent_name} - "
        f"{match.result.upper()} "
        f"{match.wrestler_score}-{match.opponent_score}"
    )


def add_match(tracker, repository):
    """Ask for a match's details, add it to the tracker, and save the season.

    A tie is rejected by WrestlingMatch, in which case nothing is added or
    saved.

    Args:
        tracker: The SeasonTracker that receives the new match.
        repository: The MatchRepository used to save the season.
    """
    opponent_name = prompt_for_opponent_name()
    wrestler_score = prompt_for_score("Your score: ")
    opponent_score = prompt_for_score("Opponent score: ")

    print()
    try:
        match = WrestlingMatch(opponent_name, wrestler_score, opponent_score)
    except MatchValidationError as error:
        print(error)
        return

    tracker.add_match(match)
    print(
        f"Match recorded: {match.result.upper()} "
        f"{match.wrestler_score}-{match.opponent_score}"
    )

    # Saved immediately so a crash later cannot lose the match.
    try:
        repository.save(tracker.get_history())
    except DataPersistenceError as error:
        print(f"Warning: the match could not be saved. {error}")


def view_matches(tracker):
    """Print every recorded match, or a message if there are none.

    Args:
        tracker: The SeasonTracker to read from.
    """
    print()
    matches = tracker.get_history()
    if not matches:
        print("No matches recorded yet.")
        return

    print("MATCH HISTORY")
    for match_number, match in enumerate(matches, start=1):
        print(format_match(match_number, match))


def view_statistics(tracker):
    """Print the season statistics, or a message if there are no matches.

    Args:
        tracker: The SeasonTracker to read from.
    """
    print()
    statistics = tracker.get_statistics()
    if statistics["total_matches"] == 0:
        print("No matches recorded yet.")
        return

    print("SEASON STATISTICS")
    print()
    print(f"Matches: {statistics['total_matches']}")
    print(f"Wins: {statistics['wins']}")
    print(f"Losses: {statistics['losses']}")
    print(f"Win Percentage: {statistics['win_percentage']:.1f}%")
    print(f"Points Scored: {statistics['total_points']}")
    print(f"Average Points: {statistics['average_points']:.1f}")


def search_opponent(tracker):
    """Ask for a name and print every match whose opponent contains it.

    Args:
        tracker: The SeasonTracker to search.
    """
    search_name = input("Opponent name to search for: ").strip()
    print()
    if search_name == "":
        print("Search name cannot be empty.")
        return

    results = tracker.search_opponents(search_name)
    if not results:
        print(f"No matches found for '{search_name}'.")
        return

    print(f"MATCHES FOR '{search_name}'")
    for match_number, match in results:
        print(format_match(match_number, match))


def run_menu(tracker, repository):
    """Show the menu repeatedly and carry out the user's choices until Exit.

    Args:
        tracker: The SeasonTracker holding the season's matches.
        repository: The MatchRepository used to save new matches.
    """
    running = True

    while running:
        display_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_match(tracker, repository)
        elif choice == "2":
            view_matches(tracker)
        elif choice == "3":
            view_statistics(tracker)
        elif choice == "4":
            search_opponent(tracker)
        elif choice == "5":
            print("Goodbye!")
            running = False
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


def main(repository=None):
    """Load the saved season, then run the menu until the user exits.

    If the data file exists but cannot be loaded, the program explains why
    and stops without touching the file, so damaged data is never overwritten.
    Ending the input (Ctrl+D) or pressing Ctrl+C exits quietly instead of
    showing a traceback; matches are saved as soon as they are added, so
    nothing recorded is lost.

    Args:
        repository: The MatchRepository to use. Defaults to a
            JsonMatchRepository for data/matches.json; tests pass their own.

    Returns:
        The exit status for the process: 0 for a normal exit (including
        closed input), 1 if the stored data could not be loaded, and 130
        if the user interrupted the program with Ctrl+C.
    """
    if repository is None:
        repository = JsonMatchRepository(DEFAULT_DATA_FILE)

    print("WRESTLING MATCH TRACKER")

    try:
        tracker = SeasonTracker(repository.load())
    except DataPersistenceError as error:
        print()
        print(f"Could not load saved matches. {error}")
        print("Fix or move the file, then start the program again.")
        return 1

    match_count = len(tracker.get_history())
    if match_count == 1:
        print("Loaded 1 saved match.")
    elif match_count > 1:
        print(f"Loaded {match_count} saved matches.")

    try:
        run_menu(tracker, repository)
    except EOFError:
        print()
        print("Input closed. Goodbye!")
    except KeyboardInterrupt:
        print()
        print("Interrupted. Goodbye!")
        return 130

    return 0
