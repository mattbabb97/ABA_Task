# ABA Abstract Rule Learning Task Capuchin Joystick Version

**Author:** Matthew H. Babb

A Python/pygame joystick adaptation of the ABA rule-learning task from Antoun, Murugan & Wilson (2025) modified for capuchin monkeys

## Overview

On each trial, three sequences of colored squares following the rules **ABA**, **AAB**, and **BAA** appear in three of the four screen corners. The A and B colors are generated fresh every trial, so the subject must learn the abstract rule rather than any specific color. One rule is assigned as correct for each monkey: correct choices are rewarded with a pellet, and incorrect choices add a timeout.

Color pairs are selected to remain distinguishable for red-green colorblind (dichromat) capuchins. The task runs continuously, records every trial, and tracks daily performance toward the learning criterion (≥70% correct on 3 of 5 consecutive testing days).

## Files

| File | Description |
|------|-------------|
| `ABA_Color_Training_v2.py` | Main task script |
| `Capuchin_Colors.py` | Generates colorblind-safe color pairs |
| `Matts_Toolbox.py` | Shared functions for screen, joystick, pellets, and data files |
| `parameters.txt` | Task settings editable by research assistants (full screen, rule, ITI, timeout, pellets) |
| `monkey.txt` | Name of the subject being tested |
| `total_trials.txt` | Running count of all completed trials |
| `ABA_Variable_Definitions.csv` | Definitions of every data column |
| `*.wav`, `*.png` | Sound files and window icon |
| `File Reset/` | Blank `total_trials.txt` for starting a new subject |
| `Old Versions/` | Previous versions of the task |

## Output

| File | Description |
|------|-------------|
| `MONKEY_ABA_Color_DATE.csv` | Trial-by-trial data, one file per testing day |
| `MONKEY_Testing_Day_Summary.csv` | Daily summary for each testing day with 100+ trials |

## Requirements

- Python 3
- [pygame](https://www.pygame.org/)
- tkinter (included with standard Python installations on Windows)
- Joystick (arrow keys are used if no joystick is connected)
- Pellet dispenser controlled by `c:\pellet.exe` (the task runs without it)
