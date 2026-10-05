"""
Wrestling Match Tracker
Author: Aayush
Purpose: Contains the main program for recording and analyzing wrestling matches.
Starter Code/Resources: None
Date: 2026-10-04
"""

print("===== WRESTLING MATCH TRACKER =====")

# Program state: every recorded match is stored as a dictionary in this list.
matches = []

# Program state: the loop keeps running until the user chooses Exit.
running = True

while running:
    print()
    print("1. Add Match")
    print("2. View Matches")
    print("3. View Season Statistics")
    print("4. Search Opponent")
    print("5. Exit")

    choice = input("Choose an option (1-5): ")

    if choice == "1":
        # Keep asking for the opponent name until it is not empty.
        opponent_name = ""
        while opponent_name == "":
            opponent_name = input("Opponent name: ").strip()
            if opponent_name == "":
                print("Opponent name cannot be empty.")

        # Keep asking for the score until it is a whole number that is not
        # negative. isdigit() is False for "-3", so negatives are checked
        # separately to give a more helpful message.
        user_score = None
        while user_score is None:
            score_text = input("Your score: ").strip()
            if score_text.isdigit():
                user_score = int(score_text)
            elif score_text.startswith("-") and score_text[1:].isdigit():
                print("Score cannot be negative.")
            else:
                print("Please enter a whole number.")

        opponent_score = None
        while opponent_score is None:
            score_text = input("Opponent score: ").strip()
            if score_text.isdigit():
                opponent_score = int(score_text)
            elif score_text.startswith("-") and score_text[1:].isdigit():
                print("Score cannot be negative.")
            else:
                print("Please enter a whole number.")

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
    elif choice == "2":
        print()
        if len(matches) == 0:
            print("No matches recorded yet.")
        else:
            print("===== MATCH HISTORY =====")
            match_number = 1
            for match in matches:
                print(
                    f"{match_number}. {match['opponent']} - "
                    f"{match['result'].upper()} "
                    f"{match['user_score']}-{match['opponent_score']}"
                )
                match_number += 1
    elif choice == "3":
        print()
        if len(matches) == 0:
            print("No matches recorded yet.")
        else:
            total_matches = len(matches)
            win_count = 0
            loss_count = 0
            total_points = 0

            for match in matches:
                if match["result"] == "Win":
                    win_count += 1
                else:
                    loss_count += 1
                total_points += match["user_score"]

            # Only reached when matches is not empty, so no division by zero.
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
    elif choice == "4":
        search_name = input("Opponent name to search for: ").strip()
        print()
        if search_name == "":
            print("Search name cannot be empty.")
        else:
            # lower() makes the search ignore capitalization, and "in" lets a
            # partial name such as "john" find "John Smith".
            search_text = search_name.lower()
            found_count = 0
            match_number = 1
            for match in matches:
                if search_text in match["opponent"].lower():
                    if found_count == 0:
                        print(f"===== MATCHES FOR '{search_name}' =====")
                    print(
                        f"{match_number}. {match['opponent']} - "
                        f"{match['result'].upper()} "
                        f"{match['user_score']}-{match['opponent_score']}"
                    )
                    found_count += 1
                match_number += 1

            if found_count == 0:
                print(f"No matches found for '{search_name}'.")
    elif choice == "5":
        print("Goodbye!")
        running = False
    else:
        print("Invalid choice. Please enter a number from 1 to 5.")
