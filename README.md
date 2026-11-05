# ABA Abstract Rule Learning Task Capuchin Joystick Version

**Author:** Matthew H. Babb

A Python/pygame joystick adaptation of the ABA rule-learning task from Antoun, Murugan & Wilson (2025) modified for capuchin monkeys

## Overview

On each trial, three sequences following the rules **ABA**, **AAB**, and **BAA** appear in three of the four screen corners. One rule is assigned as correct for each monkey (set in `parameters.txt`). The task runs continuously and records every trial. It has two phases:

### Phase 1: Color Rule Training (`ABA_Color_Training_v2.py`)

Each sequence is made of colored squares. The A and B colors are generated fresh every trial, so the subject must learn the abstract rule rather than any specific color. Correct choices are rewarded with a pellet, and incorrect choices add a timeout. Color pairs are selected to remain distinguishable for red-green colorblind (dichromat) capuchins. The script tracks daily performance toward the learning criterion (≥70% correct on 3 of 5 consecutive testing days).

### Phase 2: Color to Shape Generalization Test (`ABA_Color_Shape_Test_v1.py`)

Run once a monkey reaches criterion in Phase 1. Trials come in blocks of 10:

- **9 color trials:** identical to Phase 1 (same feedback, pellets, and timeouts)
- **1 shape probe trial**, at a random spot in the block: the sequences are made of white shapes on black backgrounds (`stimuli/A###.png` and `B###.png`) instead of colored squares. There is no sound or colored feedback screen, and the monkey gets a pellet no matter which sequence it chooses. A choice is scored correct if it matches the monkey's color rule.

Each of the 500 shape pairs is shown exactly once. The A shape always fills the A positions (shown twice in ABA) and the B shape fills the B position. The first time the script runs, it shuffles `probe_trial_order.txt`; probe trial *n* then uses the pair listed on row *n*. Shape probes have their own corner rotation, so the correct shape sequence lands in each corner about equally often.

Testing can be spread across as many days as needed. Progress is saved after every trial, and the script picks up where the monkey left off (including partway through a block) without repeating a shape pair. The test ends after the block that contains the 500th probe (500 blocks, 5,000 trials). A popup then tells the research assistant to text Nicole, and the program closes.

## Files

| File | Description |
|------|-------------|
| `ABA_Color_Training_v2.py` | Phase 1 script: color rule training |
| `ABA_Color_Shape_Test_v1.py` | Phase 2 script: color trials with shape probe trials |
| `Capuchin_Colors.py` | Generates colorblind-safe color pairs |
| `Matts_Toolbox.py` | Shared functions for screen, joystick, pellets, and data files |
| `parameters.txt` | Task settings editable by research assistants (full screen, rule, ITI, timeout, pellets) |
| `monkey.txt` | Name of the subject being tested |
| `total_trials.txt` | Running count of all completed Phase 1 (training) trials. Not changed by Phase 2 |
| `testing_blocks.txt` | Phase 2: number of 10-trial testing blocks completed |
| `probe_trials_completed.txt` | Phase 2: number of shape probe trials completed (test ends at 500) |
| `probe_trial_order.txt` | Phase 2: order of the 500 shape pairs (1–500 until the first test session shuffles it) |
| `stimuli/` | Shape stimuli: 500 pairs, `A1.png`–`A500.png` and `B1.png`–`B500.png` |
| `ABA_Variable_Definitions.csv` | Definitions of every Phase 1 data column |
| `ABA_Color_Shape_Test_Variable_Definitions.csv` | Definitions of every Phase 2 data column |
| `*.wav`, `*.png` | Sound files and window icon |
| `File Reset/` | Blank counter files and an unshuffled `probe_trial_order.txt` for starting a new subject |
| `Old Versions/` | Previous versions of the task |

Each monkey runs from its own copy of this folder.

## Output

| File | Description |
|------|-------------|
| `MONKEY_ABA_Color_DATE.csv` | Phase 1 trial-by-trial data, one file per testing day |
| `MONKEY_Testing_Day_Summary.csv` | Phase 1 daily summary for each testing day with 100+ trials |
| `MONKEY_ABA_Color_Shape_Test_DATE.csv` | Phase 2 trial-by-trial data, one file per testing day. Includes trial type (`color trial` / `shape trial`), probe number, and shape pair |
| `MONKEY_Color_Shape_Test_Summary.csv` | Phase 2 daily summary: % correct on color trials and % rule choices on shape probes (chance = 33.3%) |

Keep the Phase 2 data files in the task folder until testing is finished: the script reads them to find where the monkey left off.

## Starting Phase 2 for a monkey

1. Confirm the monkey reached criterion in Phase 1 and that `parameters.txt` still has its rule.
2. Make sure `testing_blocks.txt` and `probe_trials_completed.txt` both say `0`, and `probe_trial_order.txt` is 1–500 in order (copy them from `File Reset/` if needed).
3. Run `ABA_Color_Shape_Test_v1.py`.

## Requirements

- Python 3
- [pygame](https://www.pygame.org/)
- tkinter (included with standard Python installations on Windows)
- Joystick (arrow keys are used if no joystick is connected)
- Pellet dispenser controlled by `c:\pellet.exe` (the task runs without it)
