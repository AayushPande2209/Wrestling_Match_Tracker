"""
Wrestling Match Tracker
Author: Aayush Pande
Purpose: Contains the main program for recording and analyzing wrestling matches.
Starter Code/Resources: None
Date: 2026-10-04
"""


def display_menu():
    """Print the main menu options."""
    print()
    print("1. Add Match")
    print("2. View Matches")
    print("3. View Season Statistics")
    print("4. Search Opponent")
    print("5. Exit")


def get_opponent_name():
    """Keep asking until the user enters a non-empty opponent name."""
    opponent_name = ""
    while opponent_name == "":
        opponent_name = input("Opponent name: ").strip()
        if opponent_name == "":
            print("Opponent name cannot be empty.")
    return opponent_name


def get_score(prompt):
    """Keep asking until the user enters a non-negative whole number."""
    score = None
    while score is None:
        score_text = input(prompt).strip()
        # isdecimal() is False for "-3", so negatives are checked separately
        # to give a more helpful message. (isdigit() is not used because it
        # accepts characters such as "²" that int() cannot convert.)
        if score_text.isdecimal():
            score = int(score_text)
        elif score_text.startswith("-") and score_text[1:].isdecimal():
            print("Score cannot be negative.")
        else:
            print("Please enter a whole number.")
    return score


def add_match(matches):
    """Ask for a match's details, then store it in the matches list."""
    opponent_name = get_opponent_name()
    user_score = get_score("Your score: ")
    opponent_score = get_score("Opponent score: ")

    # Wrestling matches always have a winner, so equal scores are not saved.
    if user_score == opponent_score:
        print()
        print("Matches cannot end in a tie. Match not recorded.")
        return

    if user_score > opponent_score:
        result = "Win"
    else:
        result = "Loss"

    match = {
        "opponent": opponent_name,
        "user_score": user_score,
        "opponent_score": opponent_score,
        "result": result,
    }
    matches.append(match)

    print()
    print(f"Match recorded: {result.upper()} {user_score}-{opponent_score}")


def format_match(match, match_number):
    """Return one match as text, such as '1. John Smith - WIN 8-4'."""
    return (
        f"{match_number}. {match['opponent']} - "
        f"{match['result'].upper()} "
        f"{match['user_score']}-{match['opponent_score']}"
    )


def view_matches(matches):
    """Print every recorded match, or a message if there are none."""
    print()
    if len(matches) == 0:
        print("No matches recorded yet.")
        return

    print("===== MATCH HISTORY =====")
    match_number = 1
    for match in matches:
        print(format_match(match, match_number))
        match_number += 1


def calculate_statistics(matches):
    """Return the win count, loss count, and total points from the matches."""
    win_count = 0
    loss_count = 0
    total_points = 0

    for match in matches:
        if match["result"] == "Win":
            win_count += 1
        else:
            loss_count += 1
        total_points += match["user_score"]

    # Returning several values at once gives a tuple, which is unpacked by
    # the caller.
    return win_count, loss_count, total_points


def view_statistics(matches):
    """Print the season statistics, or a message if there are no matches."""
    print()
    total_matches = len(matches)
    if total_matches == 0:
        print("No matches recorded yet.")
        return

    win_count, loss_count, total_points = calculate_statistics(matches)
    win_percentage = win_count / total_matches * 100
    average_points = total_points / total_matches

    print("===== SEASON STATISTICS =====")
    print()
    print(f"Matches: {total_matches}")
    print(f"Wins: {win_count}")
    print(f"Losses: {loss_count}")
    print(f"Win Percentage: {win_percentage:.1f}%")
    print(f"Points Scored: {total_points}")
    print(f"Average Points: {average_points:.1f}")


def search_opponent(matches):
    """Ask for a name and print every match whose opponent name contains it."""
    search_name = input("Opponent name to search for: ").strip()
    print()
    if search_name == "":
        print("Search name cannot be empty.")
        return

    # lower() makes the search ignore capitalization, and "in" lets a
    # partial name such as "john" find "John Smith".
    search_text = search_name.lower()
    found_count = 0
    match_number = 1
    for match in matches:
        if search_text in match["opponent"].lower():
            if found_count == 0:
                print(f"===== MATCHES FOR '{search_name}' =====")
            print(format_match(match, match_number))
            found_count += 1
        match_number += 1

    if found_count == 0:
        print(f"No matches found for '{search_name}'.")


def main():
    """Run the menu loop until the user chooses Exit."""
    print("===== WRESTLING MATCH TRACKER =====")

    # Program state: every recorded match is a dictionary in this list.
    matches = []
    running = True

    while running:
        display_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_match(matches)
        elif choice == "2":
            view_matches(matches)
        elif choice == "3":
            view_statistics(matches)
        elif choice == "4":
            search_opponent(matches)
        elif choice == "5":
            print("Goodbye!")
            running = False
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


main()
