"""
Wrestling Match Tracker
Author: Aayush
Purpose: Contains the main program for recording and analyzing wrestling matches.
Starter Code/Resources: None
Date: 2026-10-04
"""

print("===== WRESTLING MATCH TRACKER =====")

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
        print("This feature is not available yet.")
    elif choice == "2":
        print("This feature is not available yet.")
    elif choice == "3":
        print("This feature is not available yet.")
    elif choice == "4":
        print("This feature is not available yet.")
    elif choice == "5":
        print("Goodbye!")
        running = False
    else:
        print("Invalid choice. Please enter a number from 1 to 5.")
