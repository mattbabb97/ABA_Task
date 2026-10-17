ABA ABSTRACT RULE LEARNING TASK - CAPUCHIN JOYSTICK VERSION
Matthew H. Babb

Python/pygame joystick version of the ABA task from Antoun, Murugan & Wilson (2025)

WHAT THE TASK DOES
Each trial, three sequences of colored squares (ABA, AAB, BAA) appear in 3 of the 4 screen corners.
The A and B colors are new every trial, so the monkey must learn the abstract rule, not the colors.
One rule is "correct" for each monkey. Correct choices earn a pellet; incorrect choices add a timeout.
Colors are chosen to be distinguishable for red-green colorblind (dichromat) capuchins.
The task runs continuously, logs every trial, and tracks daily performance toward criterion
(70% correct on 3 of 5 consecutive testing days).

FILES
ABA_Color_Training_v2.py      Main task. Run this.
Capuchin_Colors.py            Generates colorblind-safe color pairs
Matts_Toolbox.py              Shared functions (screen, joystick, pellets, data files)
parameters.txt                Settings for research assistants (full screen, rule, ITI, timeout, pellets)
monkey.txt                    Name of the monkey being tested
total_trials.txt              Running count of all trials completed
ABA_Variable_Definitions.csv  Description of every data column
*.wav / *.png                 Sounds and window icon
File Reset/                   Blank copy of total_trials.txt for starting a new monkey
Old Versions/                 Previous versions of the task

OUTPUT
MONKEY_ABA_Color_DATE.csv          One row per trial
MONKEY_Testing_Day_Summary.csv     One row per testing day with 100+ trials

REQUIREMENTS
Python 3
pygame
tkinter (included with standard Python on Windows)
Joystick (arrow keys work if none is connected)
Pellet dispenser run by c:\pellet.exe (the task still runs without it)
