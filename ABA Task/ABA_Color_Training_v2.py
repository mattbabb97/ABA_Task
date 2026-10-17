#     _    ____    _        _____         _
#    / \  | __ )  / \      |_   _|_ _ ___| | __
#   / _ \ |  _ \ / _ \       | |/ _` / __| |/ /
#  / ___ \| |_) / ___ \      | | (_| \__ \   <
# /_/   \_\____/_/   \_\     |_|\__,_|___/_|\_\
# CODE BY MATTHEW H. BABB ALL RIGHTS RESERVED !!!!!!!!!!!!
# Do NOT use this code without the permission of original creator. That is me. I am creator. Email me at matthew.h.babb@gmail.com if you have quesitons !!!!!!!!!!!!

import sys                  # Import the 'system' library
import os                   # Import the operating system (OS)

# Make sure we are running inside the task folder (Matt's Toolbox needs monkey.txt and the .wav files from here)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import random               # Import the 'random' library which gives cool functions for randomizing numbers
import time                 # Import the 'time' library for functions of keeping track of time (ITIs, IBIs etc.)
import csv                  # Import the 'csv' library to read old data files and write the summary file
import pygame               # Import Pygame to have access to all those cool functions
import Matts_Toolbox        # Import Matt's Toolbox with LRC specific functions
import Capuchin_Colors      # Import the capuchin-safe (red-green colorblind friendly) color generator

pygame.init()               # This initializes all pygame modules

"""READ FILES ------------------------------------------------------------------------------------------------------"""

# Read the monkey name from monkey.txt
with open("monkey.txt") as f:
    monkey = f.read().strip()
version = "ABA_COLOR_v2"                                        # Update this for new versions
# Set Current Date
today = time.strftime('%Y-%m-%d')

"""SET UP LOCAL VARIABLES ---------------------------------------------------------------------------------------------"""

white = (255, 255, 255)                                         # This sets up colors you might need
black = (0, 0, 0)                                               # Format is (Red, Green, Blue)
dark_grey = (40, 40, 40)                                        # Background
frame_grey = (150, 150, 150)                                    # Border around each sequence
light_orange = (255, 200, 130)                                  # Phase 2 background for CORRECT
light_blue = (170, 215, 255)                                    # Phase 2 background for INCORRECT
cursor_white = (250, 250, 250)                                  # NOT (255, 255, 255): Box() makes pure white invisible

"""Put your sounds here"""
sound_chime = pygame.mixer.Sound("chime.wav")                   # This sets trial initiation sound
                                                                # correct.wav and Incorrect.wav are played by sound() in Matt's Toolbox

"""Put your Screen Parameters here"""
scrSize = (800, 600)                                            # Standard Resolution of Monkey Computers is 800 x 600
scrRect = pygame.Rect((0, 0), scrSize)                          # Sets the shape of the screen to be a rectangle
fps = 60                                                        # Frames Per Second. Changing this changes the cursor speed.
cursor_start = (400, 300)                                       # Dead center of the screen

"""Stimulus Locations"""
# All 4 corners are 250 pixels from the cursor start (225 across, 200 up/down)
location_xy = {1: (175, 100),                                   # 1 = top-left
               2: (625, 100),                                   # 2 = top-right
               3: (175, 500),                                   # 3 = bottom-left
               4: (625, 500)}                                   # 4 = bottom-right
location_name = {1: 'top-left', 2: 'top-right', 3: 'bottom-left', 4: 'bottom-right'}

"""Stimulus Size variables"""
element_size = 60                                               # Each colored square is 60 x 60 pixels
element_gap = 10                                                # Gap between the 3 squares
frame_padding = 10                                              # Space between the squares and the border
frame_width = 3                                                 # Thickness of the border
                                                                # Total sequence size = 220 x 80 pixels

"""Task Settings"""
cursor_speed = 4
trials_for_summary = 100                                        # Trials needed in 1 day for that day to count in the summary
criterion_pct = 70.0                                            # Criterion: 70% correct...
criterion_days_needed = 3                                       # ...on 3...
criterion_days_window = 5                                       # ...of the last 5 testing days
summary_file = monkey + "_Testing_Day_Summary.csv"
total_trials_file = "total_trials.txt"

# Which 2 sequences are the foils (incorrect) for each rule
foil_lookup = {"ABA": ["AAB", "BAA"],
               "AAB": ["ABA", "BAA"],
               "BAA": ["ABA", "AAB"]}

# Each sequence as a number for easy analysis
sequence_number = {"ABA": 1,
                   "AAB": 2,
                   "BAA": 3}


"""FILE MANIPULATION FUNCTIONS --------------------------------------------------------------------------------------"""

# Create an Output File
from Matts_Toolbox import writeLn

# Name the file of your Data Output
from Matts_Toolbox import makeFileName

# Get parameters from parameters.txt
from Matts_Toolbox import getParams

"""SCREEN MANIPULATION FUNCTIONS ------------------------------------------------------------------------------------"""
from Matts_Toolbox import setScreen

from Matts_Toolbox import refresh

"""HELPER FUNCTIONS -------------------------------------------------------------------------------------------------"""
# Quit Program Function
from Matts_Toolbox import quitEscQ

# Sound Playing Function
from Matts_Toolbox import sound

# Pellet Dispensing Function
from Matts_Toolbox import pellet

# Moving the Cursor
from Matts_Toolbox import joyCount
from Matts_Toolbox import moveCursor

# Capuchin-safe color pair generator (see Capuchin_Colors.py)
from Capuchin_Colors import capuchin_color_pair

"""LIST OF TODOS ----------------------------------------------------------------------------------------------------"""

# NONE

"""SUMMARY AND CRITERIA FUNCTIONS ------------------------------------------------------------------------------------"""

def count_todays_trials(filename):
    """If the program was already run today (restart, crash, etc.), count the trials already in today's data file.
       Returns: number of trials today, number correct today"""
    trials = 0
    correct = 0
    if not os.path.isfile(filename):
        return trials, correct
    with open(filename, 'r') as data:
        reader = csv.reader(data)
        header = next(reader, None)
        if header is None:
            return trials, correct
        correct_column = header.index('correct')
        for row in reader:
            if len(row) > correct_column and row[0] != 'monkey':     # Skip blank lines and extra header rows
                trials += 1
                correct += int(row[correct_column])
    return trials, correct


def update_summary(trials_today, correct_today):
    """Rewrite TODAY's row in MONKEYNAME_Testing_Day_Summary.csv. Runs after every trial but only onnce 100 trials are done,
       so the file is always up to date"""
    percent = round((correct_today / float(trials_today)) * 100, 1)
    header = ['monkey', 'date', 'trials_completed', 'trials_correct', 'percent_correct']
    rows = []
    if os.path.isfile(summary_file):
        with open(summary_file, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)                                          # Skip the header
            for row in reader:
                if len(row) >= 5 and row[1] != today:                   # Keep every day except today
                    rows.append(row)
    rows.append([monkey, today, trials_today, correct_today, percent])  # Add today's (updated) row at the end
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def check_criteria():
    """Look at the last 5 testing days in the summary file.
       Returns True if the monkey got >= 70% on at least 3 of them"""
    if not os.path.isfile(summary_file):
        return False
    rows = []
    with open(summary_file, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 5:
                rows.append(row)
    last_days = rows[-criterion_days_window:]                          # The last 5 testing days (or fewer if < 5 exist)
    days_passed = 0
    for row in last_days:
        if float(row[4]) >= criterion_pct:
            days_passed += 1
    print("Criteria check: " + str(days_passed) + " of the last " + str(len(last_days)) + " testing days >= " + str(criterion_pct) + "%")
    return days_passed >= criterion_days_needed


def criteria_popup():
    """Pop up a window for the research assistant. They press OK and the task runs as normal"""
    message = ("This monkey reached criteria on the task. Please text Nicole at 470-530-4243 to let her know. "
               "Press okay to continue.")
    try:
        import tkinter
        from tkinter import messagebox
        root = tkinter.Tk()
        root.withdraw()                                                 # Hide the empty main tkinter window
        root.attributes('-topmost', True)                               # Keep the popup in front of everything
        messagebox.showinfo("ABA Task - Criteria Reached", message, parent=root)
        root.destroy()
    except Exception as e:
        # Back-up plan if tkinter is not installed: show the message on the pygame screen instead
        print("tkinter popup did not work (" + str(e) + "), using pygame message instead")
        temp_screen = setScreen(full_screen)
        font = pygame.font.SysFont(None, 32)
        lines = ["This monkey reached criteria on the task.",
                 "Please text Nicole at 470-530-4243 to let her know.",
                 "Press ENTER (or click) to continue."]
        temp_screen.fill(white)
        for i, line in enumerate(lines):
            text = font.render(line, True, black)
            temp_screen.blit(text, text.get_rect(center=(400, 250 + i * 40)))
        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


"""POSITION RANDOMIZATION FUNCTION ----------------------------------------------------------------------------------"""

def pseudorandomize_positions(array, configs, previous_locations):
    """Shuffle the position configurations so the CORRECT sequence is never in the same corner more than 3 trials
       in a row. previous_locations = correct corners of the last 3 trials of the previous block, so this also
       works across the switch from one block to the next"""
    while True:
        random.shuffle(array)
        correct_locations = previous_locations + [configs[c][0] for c in array]
        passed = True
        for i in range(3, len(correct_locations)):
            if correct_locations[i] == correct_locations[i - 1] == correct_locations[i - 2] == correct_locations[i - 3]:
                passed = False
                break
        if passed:
            return array


""" SEQUENCE CLASS ---------------------------------------------------------------------------------------------------"""

from Matts_Toolbox import Box

class Sequence(Box):
    def __init__(self, grammar, color_A, color_B, location):
        super(Sequence, self).__init__()
        self.grammar = grammar                                                  # "ABA", "AAB", or "BAA"
        self.location = location                                                # 1 - 4 (see location_xy)
        width = 3 * element_size + 2 * element_gap + 2 * frame_padding
        height = element_size + 2 * frame_padding

        self.image = pygame.Surface((width, height))
        self.image.fill(dark_grey)
        pygame.draw.rect(self.image, frame_grey, (0, 0, width, height), frame_width)      # Border

        for i, letter in enumerate(grammar):                                    # Draw the 3 colored squares
            if letter == "A":
                color = color_A
            else:
                color = color_B
            x = frame_padding + i * (element_size + element_gap)
            pygame.draw.rect(self.image, color, (x, frame_padding, element_size, element_size))

        self.rect = self.image.get_rect()
        self.rect.center = self.position = location_xy[location]
        self.mask = pygame.mask.from_surface(self.image)                        # Whole rectangle is touchable

    """This function allows you to move the Sequence anywhere on the screen"""
    def mv2pos(self, position):
        self.rect = self.image.get_rect()
        self.rect.center = self.position = position

# Alright monkeys...time to run the task. get to it!!

""" TRIAL CLASS -----------------------------------------------------------------------------------------------------"""
class Trial(object):
    def __init__(self):
        super(Trial, self).__init__()
        self.rule = rule                                    # The correct sequence for this monkey (parameters.txt)
        self.foils = foil_lookup[self.rule]                 # The 2 incorrect sequences
        self.trial_number = 0                               # Trial number for this time the program was opened
        self.trial_within_block = -1                        # Trial Within the current block {0 - 23}
        self.block = 1                                      # Block number {1 - x}
        self.block_length = 24                              # 24 position configurations = 1 block
        self.start_time = 0
        self.feedback_start = 0

        # Keep track of trial counts
        with open(total_trials_file) as t:
            self.total_trials = int(t.read().strip())       # Every trial this monkey has ever done on this task
        self.trials_today, self.correct_today = count_todays_trials(data_file)
        print("Total trials so far: " + str(self.total_trials))
        print("Trials already done today: " + str(self.trials_today) + " (" + str(self.correct_today) + " correct)")

        # Keep Track of Phases
        self.phase1 = False                                 # Phase 1: Show the 3 sequences, wait for a choice
        self.phase2 = False                                 # Phase 2: Feedback (selected sequence + colored background)

        # Keep Track of events that occur inside the program
        self.event1 = False                                 # event1 = sound + pellet already given this trial

        # Position configurations: (correct corner, foil 1 corner, foil 2 corner)
        # 1 = top-left, 2 = top-right, 3 = bottom-left, 4 = bottom-right
        # Every combination once per block of 24, so each corner is correct 6 times per block
        self.position_configs = {1: (1, 2, 3),   2: (1, 2, 4),   3: (1, 3, 2),   4: (1, 3, 4),   5: (1, 4, 2),   6: (1, 4, 3),
                                 7: (2, 1, 3),   8: (2, 1, 4),   9: (2, 3, 1),  10: (2, 3, 4),  11: (2, 4, 1),  12: (2, 4, 3),
                                 13: (3, 1, 2), 14: (3, 1, 4),  15: (3, 2, 1),  16: (3, 2, 4),  17: (3, 4, 1),  18: (3, 4, 2),
                                 19: (4, 1, 2), 20: (4, 1, 3),  21: (4, 2, 1),  22: (4, 2, 3),  23: (4, 3, 1),  24: (4, 3, 2)}
        self.icon_position_array = list(range(1, 25))
        pseudorandomize_positions(self.icon_position_array, self.position_configs, [])

        self.stimuli = []

    """Now that you have created your "Trial" class and given it all the attributes you want, it is time to give all objects of the "Trial" class access to FUNCTIONS"""

    def new(self):
        """Start a new trial"""
        global SELECT
        print("----------------------------------------------------")
        SELECT = -1
        self.trial_number += 1
        self.trial_within_block += 1

        if self.trial_within_block == self.block_length:                        # If this is the last trial in the block
            self.trial_within_block = 0                                         # Reset this to 0
            self.newBlock()                                                     # Run the function .newBlock()

        # Reset all phases and events
        self.phase1 = True
        self.phase2 = False
        self.event1 = False

        self.create_stimuli()                                                   # Run the function .create_stimuli()
        cursor.mv2pos(cursor_start)                                             # Move the cursor to dead center
        sound_chime.play()                                                      # Chime = new trial

        print("Trial (today): " + str(self.trials_today + 1) + "   Total: " + str(self.total_trials + 1))
        print("Block: " + str(self.block) + "   Trial_within_block: " + str(self.trial_within_block + 1) + " out of " + str(self.block_length))
        print("Position config: " + str(self.config) + " " + str(self.position_configs[self.config]) + "   Colors A: " + str(self.color_A) + " B: " + str(self.color_B))

        self.start_time = pygame.time.get_ticks()

    def newBlock(self):
        """Moves program to the next block and re-shuffles the positions"""
        print("Block Complete! ===========================================")
        self.block += 1
        last_3 = [self.position_configs[c][0] for c in self.icon_position_array[-3:]]    # Correct corners of the last 3 trials
        pseudorandomize_positions(self.icon_position_array, self.position_configs, last_3)

    def create_stimuli(self):
        """Make brand new colors and put the 3 sequences in their corners"""
        self.config = self.icon_position_array[self.trial_within_block]
        correct_loc, foil1_loc, foil2_loc = self.position_configs[self.config]

        self.color_A, self.color_B, self.color_dE = capuchin_color_pair()

        # self.stimuli[0] is ALWAYS the correct sequence, [1] and [2] are the foils
        self.stimuli = [Sequence(self.rule, self.color_A, self.color_B, correct_loc),
                        Sequence(self.foils[0], self.color_A, self.color_B, foil1_loc),
                        Sequence(self.foils[1], self.color_A, self.color_B, foil2_loc)]

# Basic Drawing Functions -------------------------------------------------------------------------------------------------

    def draw_stimuli(self):
        """Draw all 3 sequences"""
        for stim in self.stimuli:
            stim.draw(screen)

# Time Keeping Functions -------------------------------------------------------------------------------------------------

    def response_time(self):
        """Seconds since the 3 sequences appeared"""
        seconds = ((pygame.time.get_ticks() - self.start_time) / 1000.000)
        return seconds

    def feedback_timer(self):
        """Seconds since the monkey made its choice"""
        seconds = ((pygame.time.get_ticks() - self.feedback_start) / 1000.000)
        return seconds

# Start the trial! Now its time to start each trial and move through each phase -----------------------------------------------

# Phase 1: Show the 3 sequences and wait for a choice (no time limit)
    def phase_1(self):
        global SELECT
        self.draw_stimuli()
        cursor.draw(screen)
        moveCursor(cursor)

        SELECT = cursor.collides_with_list(self.stimuli)                        # -1 = nothing, 0 = correct, 1 or 2 = foil
        if SELECT != -1:
            self.rt = round(self.response_time(), 3)
            self.selected = SELECT
            self.chosen_sequence = self.stimuli[SELECT].grammar
            self.chosen_sequence_num = sequence_number[self.chosen_sequence]  # 1 = ABA, 2 = AAB, 3 = BAA
            self.chosen_location = location_name[self.stimuli[SELECT].location]
            self.cursor_xy = cursor.position

            if SELECT == 0:
                self.correct = 1
                self.pellets = pellets_per_correct
                self.feedback_duration = ITI                                    # Correct: ITI only
                print("CORRECT! Chose " + self.chosen_sequence + " (" + self.chosen_location + ")  RT: " + str(self.rt))
            else:
                self.correct = 0
                self.pellets = 0
                self.feedback_duration = ITI + time_out                         # Incorrect: ITI + Timeout
                print("INCORRECT. Chose " + self.chosen_sequence + " (" + self.chosen_location + ")  RT: " + str(self.rt))

            # Update the trial counts
            self.trials_today += 1
            self.correct_today += self.correct
            self.total_trials += 1
            with open(total_trials_file, "w") as t:
                t.write(str(self.total_trials))

            # Save the data
            self.write(data_file)
            if self.trials_today >= trials_for_summary:
                update_summary(self.trials_today, self.correct_today)
                print("Summary updated: " + str(self.correct_today) + "/" + str(self.trials_today) + " correct today")

            self.feedback_start = pygame.time.get_ticks()
            self.phase1 = False
            self.phase2 = True

# Phase 2: Feedback. Selected sequence stays on screen, background flashes, sound + pellet, then next trial
    def phase_2(self):
        if self.correct == 1:
            screen.fill(light_orange)
        else:
            screen.fill(light_blue)
        self.stimuli[self.selected].draw(screen)                                # Only the selected sequence, no cursor

        if self.event1 == False:                                                # Only happens on the first frame of phase 2
            refresh(screen)                                                     # Show the feedback screen BEFORE the pellet
            if self.correct == 1:
                sound(True)
                pellet(self.pellets)
            else:
                sound(False)
            self.event1 = True

        if self.feedback_timer() >= self.feedback_duration:                     # After ITI (+ timeout) start the next trial
            self.new()

    def write(self, file):
        now = time.strftime('%H:%M:%S')

        # Where was each sequence this trial?
        loc = {}
        for stim in self.stimuli:
            loc[stim.grammar] = location_name[stim.location]

        data = [monkey, version, today, now, self.total_trials, self.trials_today, self.block, self.trial_within_block + 1,
                self.rule, self.config, loc["ABA"], loc["AAB"], loc["BAA"], loc[self.rule],
                self.chosen_sequence, self.chosen_sequence_num, self.chosen_location, self.correct, self.rt, self.cursor_xy[0], self.cursor_xy[1],
                self.color_A[0], self.color_A[1], self.color_A[2], self.color_B[0], self.color_B[1], self.color_B[2],
                self.color_dE, self.pellets]

        writeLn(file, data)

# UPLOAD TASK PARAMETERS ----------------------------------------------------------------------------------------------
varNames = ['full_screen', 'rule', 'ITI', 'time_out', 'pellets_per_correct']
try:
    params = getParams(varNames)
except Exception as e:
    print("ERROR reading parameters.txt: " + str(e))
    print("Check parameters.txt. RULE must have quotes around it, like \"ABA\"")
    input("Press Enter to close...")
    sys.exit()
globals().update(params)

full_screen = params['full_screen']                     # Since your parameters are stored in a dictionary
rule = params['rule']                                   # You can pull their value out with dictionary[key]
ITI = params['ITI']
time_out = params['time_out']
pellets_per_correct = params['pellets_per_correct']

if rule not in foil_lookup:
    print("ERROR: RULE in parameters.txt is " + str(rule) + ". It must be \"ABA\", \"AAB\", or \"BAA\"")
    input("Press Enter to close...")
    sys.exit()

print("Monkey: " + monkey + "   Rule: " + rule + "   ITI: " + str(ITI) + "   Timeout: " + str(time_out))


"""CREATE THE DATA FILE-------------------------------------------------------------------------------------------"""
data_file = makeFileName('ABA_Color')
if not os.path.isfile(data_file):                       # Only write the header once (if the task is restarted today, keep adding to the same file)
    writeLn(data_file, ['monkey', 'version', 'date', 'time', 'total_trial_number', 'trial_number_today', 'block', 'trial_within_block',
                        'rule', 'position_config', 'ABA_location', 'AAB_location', 'BAA_location', 'correct_location',
                        'chosen_sequence', 'chosen_sequence_num', 'chosen_location', 'correct', 'rt', 'cursor_x', 'cursor_y',
                        'A_red', 'A_green', 'A_blue', 'B_red', 'B_green', 'B_blue', 'color_deltaE_min', 'pellets'])


"""CHECK IF THE MONKEY HAS REACHED CRITERIA ----------------------------------------------------------------------------"""
# This happens BEFORE the task window opens so the popup is not hidden behind the full screen task
if check_criteria():
    criteria_popup()


# START THE CLOCK
clock = pygame.time.Clock()

# CREATE THE TASK WINDOW
screen = setScreen(full_screen)
pygame.display.set_caption("ABA Task - Color Rule Training v2")
display_icon = pygame.image.load("Monkey_Icon.png")
pygame.display.set_icon(display_icon)
screen.fill(dark_grey)

# DEFINE THE CURSOR
cursor = Box(color = cursor_white, speed = cursor_speed, circle = True)


"""SET UP IS COMPLETE - EVERYTHING BELOW THIS IS RUNNING THE MAIN PROGRAM"""


"""MAIN GAME LOOP -------------------------------------------------------------------------------------------"""
trial = Trial()             # Initialize a new Trial

trial.new()                 # Have the newly initialized trial run .new() function to begin ;)

running = True
while running:
    quitEscQ()
    screen.fill(dark_grey)
    clock.tick(fps)

    if trial.phase1 == True:
        trial.phase_1()
    elif trial.phase2 == True:
        trial.phase_2()

    refresh(screen)

# --------------------------------------------------------------------------------------------------------------------
