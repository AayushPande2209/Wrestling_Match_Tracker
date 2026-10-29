[YouTube Presentation](https://youtu.be/SqUbo4ywlB4)

# Wrestling Match Tracker

**Author:** Aayush Pande

## Overview

Wrestling Match Tracker is a command-line program for recording wrestling
matches and viewing statistics about a season. The user adds matches one at a
time (opponent name plus both scores), and the program decides whether each
match was a win or a loss. Matches can then be listed, summarized, or searched
by opponent. Everything is stored in memory while the program runs, so the
records are cleared when the program exits.

## Features

- **Add Match** - enter an opponent name, your score, and the opponent's
  score. The program records a win or loss and prints, for example,
  `Match recorded: WIN 8-4`.
- **Input validation** - empty opponent names, non-numeric scores, negative
  scores, and tied scores are rejected with a helpful message (wrestling
  matches always have a winner). Invalid scores are asked for again; a tie
  cancels the match.
- **View Matches** - shows a numbered list such as
  `1. John Smith - WIN 8-4`, or a message if nothing has been recorded.
- **View Season Statistics** - total matches, wins, losses, win percentage,
  total points scored, and average points per match.
- **Search Opponent** - find matches by opponent name. The search ignores
  capitalization and accepts part of a name, so `john`, `JOHN SMITH`, and
  `John Smith` all find the same opponent.
- **Exit** - ends the program cleanly.

## Course Concepts Demonstrated

| Concept | Where it appears |
|---|---|
| **Variables** | `opponent_name`, `user_score`, `opponent_score`, `win_count`, `loss_count`, `total_points`, and `running` hold values the program works with. |
| **Strings** | Menu text, f-strings such as `f"Match recorded: {result.upper()} ..."`, and string methods: `.strip()` removes extra spaces, `.lower()` makes the search case-insensitive, `.upper()` formats WIN/LOSS, and `.isdecimal()` / `.startswith()` check score input. The `in` operator finds a name inside another name. |
| **Numbers** | Scores are integers converted from text with `int()`. Win percentage and average points use `/`, which gives a float, and `:.1f` formats it to one decimal place. |
| **Lists** | `matches = []` holds every recorded match, grown with `.append()` and read with `len()` and `for` loops. |
| **Dictionaries** | Each match is a dictionary with the keys `"opponent"`, `"user_score"`, `"opponent_score"`, and `"result"`. Values are read by key, for example `match["user_score"]`. |
| **if / elif / else** | The menu selection in `main()`, deciding Win or Loss in `add_match()`, and the validation checks in `get_score()`. |
| **for loops** | Looping through `matches` to display them, add up the statistics, and search by name. |
| **while loops** | The main menu loop runs until the user chooses Exit, and the input functions keep asking until the answer is valid. |
| **User input** | `input()` collects every menu choice, name, and score. All input is text, so it is checked before being converted to a number. |
| **Program state** | `matches` stores the records between menu choices. The `running` flag controls when the menu loop stops. Validation loops use `score = None` to mean "no valid score yet". |
| **Functions** | The program is split into small functions, each with a docstring: `display_menu`, `get_opponent_name`, `get_score`, `add_match`, `format_match`, `view_matches`, `calculate_statistics`, `view_statistics`, `search_opponent`, and `main`. They use parameters and `return` values. |
| **Tuples** | Used once, naturally: `calculate_statistics()` returns three values (wins, losses, total points), which Python packs into a tuple and `view_statistics()` unpacks. A tuple was not used anywhere else because nothing else needed a fixed group of values. |

Concepts intentionally not used: classes, file storage, and `try/except`.
They are beyond Chapters 1-7, and the program does not need them, because the
input is checked with simple string methods instead.

## How to Run

You need Python 3 installed (developed and tested with Python 3.13). There is
nothing else to install.

1. Open a terminal in the project folder (the folder containing
   `wrestling_match_tracker.py`).
2. Run:

   ```bash
   python3 wrestling_match_tracker.py
   ```

   (On Windows you may need `python` instead of `python3`.)
3. Type a number from 1 to 5 at the menu and press Enter.

Example session:

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

## Project Structure

```text
├── wrestling_match_tracker.py   # the whole program
└── README.md
```

## Project Development

The program was built in separate phases, with one Git commit per phase after
that phase was run and tested:

1. **Initial project setup** - basic program with a title and an Exit option.
2. **Add interactive main menu** - the `while` loop and the five-option menu.
3. **Add match recording** - the `matches` list and match dictionaries.
4. **Add input validation** - rejecting empty names and bad scores.
5. **Add match history display** - the View Matches option.
6. **Add season statistics** - statistics calculated from `matches`.
7. **Add opponent search** - case-insensitive search by name.
8. **Refactor application structure** - the repeated code was moved into functions.
9. **Finalize application testing** - a full manual test found and fixed three
   bugs: tied scores were recorded as losses, menu choices with extra spaces
   were rejected, and some unusual digit characters crashed the score check.
10. **Complete project documentation** - this README.

The features before the refactor were written inline in one menu loop, and the
refactor in step 8 reorganized them into functions without changing behavior.
Testing was done manually by running the program and entering valid and invalid
input. There are no automated tests.

This project was developed with the help of an AI coding assistant (Claude
Code), working one phase at a time; all commits use the author's own Git
identity.
