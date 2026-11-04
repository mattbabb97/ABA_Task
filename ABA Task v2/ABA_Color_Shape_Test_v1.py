#     _    ____    _        _____         _
#    / \  | __ )  / \      |_   _|_ _ ___| | __
#   / _ \ |  _ \ / _ \       | |/ _` / __| |/ /
#  / ___ \| |_) / ___ \      | | (_| \__ \   <
# /_/   \_\____/_/   \_\     |_|\__,_|___/_|\_\
# CODE BY MATTHEW H. BABB ALL RIGHTS RESERVED !!!!!!!!!!!!
# Do NOT use this code without the permission of original creator. That is me. I am creator. Email me at matthew.h.babb@gmail.com if you have quesitons !!!!!!!!!!!!

# 90% standard color trials (exactly like ABA_Color_Training.py) + 10% shape probe trials
# Every testing block = 10 trials with exactly 1 shape probe somewhere random in it
# Shape probes: no sound, no colored background, pellet no matter what they choose
# The test is over after the block that holds the 500th probe (= 500 testing blocks = 5000 trials)

import sys                  # Import the 'system' library
import os                   # Import the operating system (OS)

# Make sure we are running inside the task folder (Matt's Toolbox needs monkey.txt and the .wav files from here)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import random               # Import the 'random' library which gives cool functions for randomizing numbers
import time                 # Import the 'time' library for functions of keeping track of time (ITIs, IBIs etc.)
import csv                  # Import the 'csv' library to read old data files and write the summary file
import glob                 # Import 'glob' to find all of this monkey's old test data files
import zlib                 # Import 'zlib' to turn probe_trial_order.txt into a random seed (see build_probe_configs)
import pygame               # Import Pygame to have access to all those cool functions
import Matts_Toolbox        # Import Matt's Toolbox with LRC specific functions
import Capuchin_Colors      # Import the capuchin-safe (red-green colorblind friendly) color generator

pygame.init()               # This initializes all pygame modules

"""READ FILES ------------------------------------------------------------------------------------------------------"""

# Read the monkey name from monkey.txt
with open("monkey.txt") as f:
    monkey = f.read().strip()
version = "ABA_COLOR_SHAPE_TEST_v1"                             # Update this for new versions
# Set Current Date
today = time.strftime('%Y-%m-%d')

"""SET UP LOCAL VARIABLES ---------------------------------------------------------------------------------------------"""

white = (255, 255, 255)                                         # This sets up colors you might need
black = (0, 0, 0)                                               # Format is (Red, Green, Blue)
dark_grey = (40, 40, 40)                                        # Background
frame_grey = (150, 150, 150)                                    # Border around each sequence
light_orange = (255, 200, 130)                                  # Phase 2 background for CORRECT (color trials only)
light_blue = (170, 215, 255)                                    # Phase 2 background for INCORRECT (color trials only)
cursor_white = (250, 250, 250)                                  # NOT (255, 255, 255): Box() makes pure white invisible

"""Put your sounds here"""
sound_chime = pygame.mixer.Sound("chime.wav")                   # This sets trial initiation sound (color AND shape trials)
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
color_element_size = 60                                         # Each colored square is 60 x 60 pixels (same as v2)
shape_element_size = 85                                         # Each shape is 85 x 85 pixels (stimuli are 225 x 225, shrunk to fit)
element_gap = 10                                                # Gap between the 3 elements
frame_padding = 10                                              # Space between the elements and the border
frame_width = 3                                                 # Thickness of the border
                                                                # Color sequence = 220 x 80 pixels, Shape sequence = 295 x 105 pixels
                                                                # (still fits in the corners: 27 pixels from the screen edges)
stimuli_folder = "stimuli"                                      # A1.png - A500.png and B1.png - B500.png

"""Task Settings"""
cursor_speed = 4
block_length = 10                                               # 1 testing block = 10 trials...
total_probes = 500                                              # ...with exactly 1 probe each. 500 probes = 500 blocks = 5000 trials
summary_file = monkey + "_Color_Shape_Test_Summary.csv"
testing_blocks_file = "testing_blocks.txt"                      # Number of 10-trial testing blocks COMPLETED
probes_completed_file = "probe_trials_completed.txt"            # Number of shape probe trials COMPLETED
probe_order_file = "probe_trial_order.txt"                      # Row n = which shape pair is shown on probe trial n
data_file_task = 'ABA_Color_Shape_Test'                         # Data files are MONKEY_ABA_Color_Shape_Test_DATE.csv
                                                                # total_trials.txt is TRAINING only, so this task never touches it

# Which 2 sequences are the foils (incorrect) for each rule
foil_lookup = {"ABA": ["AAB", "BAA"],
               "AAB": ["ABA", "BAA"],
               "BAA": ["ABA", "AAB"]}

# Each sequence as a number for easy analysis
sequence_number = {"ABA": 1,
                   "AAB": 2,
                   "BAA": 3}

# Position configurations: (correct corner, foil 1 corner, foil 2 corner)
# 1 = top-left, 2 = top-right, 3 = bottom-left, 4 = bottom-right
# Every combination once per set of 24, so each corner is correct 6 times per set
position_configs = {1: (1, 2, 3),   2: (1, 2, 4),   3: (1, 3, 2),   4: (1, 3, 4),   5: (1, 4, 2),   6: (1, 4, 3),
                    7: (2, 1, 3),   8: (2, 1, 4),   9: (2, 3, 1),  10: (2, 3, 4),  11: (2, 4, 1),  12: (2, 4, 3),
                    13: (3, 1, 2), 14: (3, 1, 4),  15: (3, 2, 1),  16: (3, 2, 4),  17: (3, 4, 1),  18: (3, 4, 2),
                    19: (4, 1, 2), 20: (4, 1, 3),  21: (4, 2, 1),  22: (4, 2, 3),  23: (4, 3, 1),  24: (4, 3, 2)}


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

"""COUNTER FILE FUNCTIONS -------------------------------------------------------------------------------------------"""

def read_number(filename):
    """Read the single number saved in a counter .txt file"""
    with open(filename) as f:
        return int(f.read().strip())


def write_number(filename, number):
    """Save a single number in a counter .txt file"""
    with open(filename, "w") as f:
        f.write(str(number))


def read_probe_order():
    """Read probe_trial_order.txt. Row n = the shape pair number used on probe trial n"""
    with open(probe_order_file) as f:
        order = [int(line.strip()) for line in f if line.strip() != ""]
    if sorted(order) != list(range(1, total_probes + 1)):
        print("ERROR: " + probe_order_file + " must have every number from 1 to " + str(total_probes) + " exactly once")
        input("Press Enter to close...")
        sys.exit()
    return order


def shuffle_probe_order_if_new(order, blocks_completed, probes_completed):
    """The FIRST time this monkey runs the test, shuffle probe_trial_order.txt (it starts as 1 - 500 in order).
       Only happens if no testing has been done yet AND the file is still in order, so it can never re-shuffle"""
    if blocks_completed == 0 and probes_completed == 0 and order == list(range(1, total_probes + 1)):
        random.shuffle(order)
        with open(probe_order_file, "w") as f:
            f.write("\n".join(str(n) for n in order))
        print("First test session: shuffled " + probe_order_file + ". First 5 probe pairs: " + str(order[:5]))
    return order


def count_testing_trials_done():
    """Look through ALL of this monkey's test data files and find the highest testing_trial_number.
       This is how the program knows how far into the current 10-trial block the monkey got last time"""
    trials_done = 0
    for filename in glob.glob(monkey + '_' + data_file_task + '_*.csv'):
        with open(filename, 'r') as data:
            reader = csv.reader(data)
            header = next(reader, None)
            if header is None or 'testing_trial_number' not in header:
                continue
            column = header.index('testing_trial_number')
            for row in reader:
                if len(row) > column and row[column].isdigit():         # Skip blank lines and extra header rows
                    trials_done = max(trials_done, int(row[column]))
    return trials_done


"""SUMMARY FUNCTIONS ------------------------------------------------------------------------------------------------"""

def count_todays_trials(filename):
    """If the program was already run today (restart, crash, etc.), count the trials already in today's data file.
       Returns: a dictionary of today's counts for color and shape trials"""
    counts = {'trials': 0, 'color_trials': 0, 'color_correct': 0, 'shape_trials': 0, 'shape_correct': 0}
    if not os.path.isfile(filename):
        return counts
    with open(filename, 'r') as data:
        reader = csv.reader(data)
        header = next(reader, None)
        if header is None:
            return counts
        type_column = header.index('trial_type')
        correct_column = header.index('correct')
        for row in reader:
            if len(row) > correct_column and row[0] != 'monkey':        # Skip blank lines and extra header rows
                add_to_counts(counts, row[type_column], int(row[correct_column]))
    return counts


def add_to_counts(counts, trial_type, correct):
    """Add 1 trial to today's counts"""
    counts['trials'] += 1
    if trial_type == "shape trial":
        counts['shape_trials'] += 1
        counts['shape_correct'] += correct
    else:
        counts['color_trials'] += 1
        counts['color_correct'] += correct


def percent(correct, trials):
    if trials == 0:
        return "NA"
    return round((correct / float(trials)) * 100, 1)


def update_summary(counts, probes_completed):
    """Rewrite TODAY's row in MONKEYNAME_Color_Shape_Test_Summary.csv. Runs after every trial so the file is always up to date.
       color_percent_correct = how they are doing on the standard color trials (should stay high)
       shape_percent_rule = how often they picked the rule sequence on shape probes (33.3% = chance)"""
    header = ['monkey', 'date', 'trials_completed', 'color_trials', 'color_correct', 'color_percent_correct',
              'shape_trials', 'shape_rule_choices', 'shape_percent_rule', 'probes_completed_total']
    rows = []
    if os.path.isfile(summary_file):
        with open(summary_file, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)                                          # Skip the header
            for row in reader:
                if len(row) >= 2 and row[1] != today:                   # Keep every day except today
                    rows.append(row)
    rows.append([monkey, today, counts['trials'],
                 counts['color_trials'], counts['color_correct'], percent(counts['color_correct'], counts['color_trials']),
                 counts['shape_trials'], counts['shape_correct'], percent(counts['shape_correct'], counts['shape_trials']),
                 probes_completed])
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def all_done_popup():
    """The monkey finished all 500 probes. Tell the research assistant, then shut the program down"""
    message = ("This monkey has finished the Shape Test (all " + str(total_probes) + " probe trials). "
               "Please text Nicole at 470-530-4243 to let her know. Press okay to close the program.")
    print("=====================================================")
    print("TEST COMPLETE: " + str(total_probes) + " probe trials done")
    pygame.quit()                                                       # Close the full screen task so the popup is not hidden behind it
    try:
        import tkinter
        from tkinter import messagebox
        root = tkinter.Tk()
        root.withdraw()                                                 # Hide the empty main tkinter window
        root.attributes('-topmost', True)                               # Keep the popup in front of everything
        messagebox.showinfo("ABA Task - Test Complete", message, parent=root)
        root.destroy()
    except Exception as e:
        # Back-up plan if tkinter is not installed: show the message in the console window instead
        print("tkinter popup did not work (" + str(e) + ")")
        print(message)
        input("Press Enter to close...")
    sys.exit()


"""POSITION RANDOMIZATION FUNCTIONS ---------------------------------------------------------------------------------"""

def pseudorandomize_positions(array, configs, previous_locations, rng=random):
    """Shuffle the position configurations so the CORRECT sequence is never in the same corner more than 3 trials
       in a row. previous_locations = correct corners of the last 3 trials of the previous set, so this also
       works across the switch from one set to the next"""
    while True:
        rng.shuffle(array)
        correct_locations = previous_locations + [configs[c][0] for c in array]
        passed = True
        for i in range(3, len(correct_locations)):
            if correct_locations[i] == correct_locations[i - 1] == correct_locations[i - 2] == correct_locations[i - 3]:
                passed = False
                break
        if passed:
            return array


def build_probe_configs(order):
    """Probe trials get their OWN position configurations: 1 config per probe trial (500 total), made of shuffled sets of 24.
       The random seed comes from this monkey's shuffled probe_trial_order.txt, so the program builds the SAME list every
       time it is opened. That way probe #n always uses config #n and the correct shape sequence ends up in each corner
       ~125 times, even when the test is spread across many days"""
    rng = random.Random(zlib.crc32(",".join(str(n) for n in order).encode()))
    configs = []
    while len(configs) < total_probes:
        new_set = list(range(1, 25))
        last_3 = [position_configs[c][0] for c in configs[-3:]]
        pseudorandomize_positions(new_set, position_configs, last_3, rng)
        configs += new_set
    return configs[:total_probes]


""" SEQUENCE CLASS ---------------------------------------------------------------------------------------------------"""

from Matts_Toolbox import Box

class Sequence(Box):
    def __init__(self, grammar, element_A, element_B, location, element_size):
        """element_A and element_B are either colors (R, G, B) for color trials or pygame images for shape trials"""
        super(Sequence, self).__init__()
        self.grammar = grammar                                                  # "ABA", "AAB", or "BAA"
        self.location = location                                                # 1 - 4 (see location_xy)
        width = 3 * element_size + 2 * element_gap + 2 * frame_padding
        height = element_size + 2 * frame_padding

        self.image = pygame.Surface((width, height))
        self.image.fill(dark_grey)
        pygame.draw.rect(self.image, frame_grey, (0, 0, width, height), frame_width)      # Border

        for i, letter in enumerate(grammar):                                    # Draw the 3 elements
            if letter == "A":
                element = element_A
            else:
                element = element_B
            x = frame_padding + i * (element_size + element_gap)
            if isinstance(element, pygame.Surface):
                self.image.blit(element, (x, frame_padding))                    # Shape: white shape on its black background
            else:
                pygame.draw.rect(self.image, element, (x, frame_padding, element_size, element_size))     # Colored square

        self.rect = self.image.get_rect()
        self.rect.center = self.position = location_xy[location]
        self.mask = pygame.mask.from_surface(self.image)                        # Whole rectangle is touchable

    """This function allows you to move the Sequence anywhere on the screen"""
    def mv2pos(self, position):
        self.rect = self.image.get_rect()
        self.rect.center = self.position = position


def load_shape(letter, pair):
    """Load A###.png or B###.png from the stimuli folder and shrink it to the shape element size"""
    image = pygame.image.load(os.path.join(stimuli_folder, letter + str(pair) + ".png")).convert()
    return pygame.transform.smoothscale(image, (shape_element_size, shape_element_size))

# Alright monkeys...time to run the task. get to it!!

""" TRIAL CLASS -----------------------------------------------------------------------------------------------------"""
class Trial(object):
    def __init__(self):
        super(Trial, self).__init__()
        self.rule = rule                                    # The correct sequence for this monkey (parameters.txt)
        self.foils = foil_lookup[self.rule]                 # The 2 incorrect sequences
        self.trial_number = 0                               # Trial number for this time the program was opened
        self.start_time = 0
        self.feedback_start = 0

        # Keep track of where the monkey is in the test (see the SET UP THE TEST section below)
        self.blocks_completed = blocks_completed            # 10-trial testing blocks finished (testing_blocks.txt)
        self.probes_completed = probes_completed            # Shape probes finished (probe_trials_completed.txt)
        self.trials_into_block = trials_into_block          # Trials already done in the current block {0 - 9}
        self.probe_order = probe_order                      # Row n = shape pair for probe n
        self.probe_configs = probe_configs                  # Position config for probe n

        # Which trial of the current block is the probe? None = this block's probe already happened (before a restart)
        if self.probes_completed > self.blocks_completed:
            self.probe_slot = None
        else:
            self.probe_slot = random.randint(self.trials_into_block, block_length - 1)

        # Keep track of today's trial counts
        self.today_counts = count_todays_trials(data_file)
        print("Testing blocks completed: " + str(self.blocks_completed) + "   Probes completed: " + str(self.probes_completed))
        print("Trials already done today: " + str(self.today_counts['trials']))

        # Keep Track of Phases
        self.phase1 = False                                 # Phase 1: Show the 3 sequences, wait for a choice
        self.phase2 = False                                 # Phase 2: Feedback (color) or just the chosen sequence (shape)

        # Keep Track of events that occur inside the program
        self.event1 = False                                 # event1 = sound + pellet already given this trial

        # Color trials: every position config once per 24 color trials (same as v2)
        self.color_position_array = list(range(1, 25))
        self.color_index = -1
        pseudorandomize_positions(self.color_position_array, position_configs, [])

        self.stimuli = []

    """Now that you have created your "Trial" class and given it all the attributes you want, it is time to give all objects of the "Trial" class access to FUNCTIONS"""

    def new(self):
        """Start a new trial"""
        global SELECT
        if self.probes_completed >= total_probes and self.trials_into_block == 0:   # Finished the block with the 500th probe
            all_done_popup()

        print("----------------------------------------------------")
        SELECT = -1
        self.trial_number += 1
        self.is_probe = (self.trials_into_block == self.probe_slot)

        # Reset all phases and events
        self.phase1 = True
        self.phase2 = False
        self.event1 = False

        self.create_stimuli()                                                   # Run the function .create_stimuli()
        cursor.mv2pos(cursor_start)                                             # Move the cursor to dead center
        sound_chime.play()                                                      # Chime = new trial

        print("Testing trial: " + str(self.testing_trial_number()) + "   Today: " + str(self.today_counts['trials'] + 1))
        print("Testing block: " + str(self.blocks_completed + 1) + "   Trial_within_block: " + str(self.trials_into_block + 1) + " out of " + str(block_length))
        if self.is_probe:
            print("SHAPE PROBE #" + str(self.probe_number) + "   Pair: " + str(self.shape_pair) + "   Position config: " + str(self.config) + " " + str(position_configs[self.config]))
        else:
            print("Position config: " + str(self.config) + " " + str(position_configs[self.config]) + "   Colors A: " + str(self.color_A) + " B: " + str(self.color_B))

        self.start_time = pygame.time.get_ticks()

    def testing_trial_number(self):
        """Trial number across the whole test {1 - 5000}"""
        return self.blocks_completed * block_length + self.trials_into_block + 1

    def create_stimuli(self):
        """Make the 3 sequences (colors or shapes) and put them in their corners"""
        if self.is_probe:
            self.probe_number = self.probes_completed + 1                       # {1 - 500}
            self.shape_pair = self.probe_order[self.probe_number - 1]           # Row n of probe_trial_order.txt
            self.config = self.probe_configs[self.probe_number - 1]
            element_A = load_shape("A", self.shape_pair)                        # A shape is always the A element (shown twice in ABA)
            element_B = load_shape("B", self.shape_pair)                        # B shape is always the B element
            element_size = shape_element_size
        else:
            self.probe_number = "NA"
            self.shape_pair = "NA"
            self.color_index += 1
            if self.color_index == len(self.color_position_array):              # Used all 24 configs: re-shuffle
                self.color_index = 0
                last_3 = [position_configs[c][0] for c in self.color_position_array[-3:]]
                pseudorandomize_positions(self.color_position_array, position_configs, last_3)
            self.config = self.color_position_array[self.color_index]
            self.color_A, self.color_B, self.color_dE = capuchin_color_pair()
            element_A = self.color_A
            element_B = self.color_B
            element_size = color_element_size

        correct_loc, foil1_loc, foil2_loc = position_configs[self.config]

        # self.stimuli[0] is ALWAYS the correct (rule) sequence, [1] and [2] are the foils
        self.stimuli = [Sequence(self.rule, element_A, element_B, correct_loc, element_size),
                        Sequence(self.foils[0], element_A, element_B, foil1_loc, element_size),
                        Sequence(self.foils[1], element_A, element_B, foil2_loc, element_size)]

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
                self.correct = 1                                                # Shape probes: 1 = chose the rule sequence
            else:
                self.correct = 0

            if self.is_probe:
                self.pellets = pellets_per_correct                              # Probe: pellet no matter what, ITI only
                self.feedback_duration = ITI
                print("SHAPE PROBE: Chose " + self.chosen_sequence + " (" + self.chosen_location + ")  Rule choice: " + str(self.correct) + "  RT: " + str(self.rt))
            elif self.correct == 1:
                self.pellets = pellets_per_correct
                self.feedback_duration = ITI                                    # Correct: ITI only
                print("CORRECT! Chose " + self.chosen_sequence + " (" + self.chosen_location + ")  RT: " + str(self.rt))
            else:
                self.pellets = 0
                self.feedback_duration = ITI + time_out                         # Incorrect: ITI + Timeout
                print("INCORRECT. Chose " + self.chosen_sequence + " (" + self.chosen_location + ")  RT: " + str(self.rt))

            # Save the probe count FIRST so a crash can never show the same shape pair twice
            if self.is_probe:
                self.probes_completed += 1
                write_number(probes_completed_file, self.probes_completed)

            # Save the data
            add_to_counts(self.today_counts, self.trial_type(), self.correct)
            self.write(data_file)
            update_summary(self.today_counts, self.probes_completed)

            # Move forward in the testing block
            self.trials_into_block += 1
            if self.trials_into_block == block_length:                          # Block finished
                self.newBlock()

            self.feedback_start = pygame.time.get_ticks()
            self.phase1 = False
            self.phase2 = True

    def newBlock(self):
        """Saves the finished block and picks where the probe goes in the next block"""
        self.blocks_completed += 1
        write_number(testing_blocks_file, self.blocks_completed)
        print("Testing Block " + str(self.blocks_completed) + " Complete! ===========================================")
        self.trials_into_block = 0
        self.probe_slot = random.randint(0, block_length - 1)

    def trial_type(self):
        if self.is_probe:
            return "shape trial"
        return "color trial"

# Phase 2: Color trials = feedback (colored background + sound). Shape probes = NO feedback, just the chosen sequence on grey
    def phase_2(self):
        if self.is_probe:
            screen.fill(dark_grey)
        elif self.correct == 1:
            screen.fill(light_orange)
        else:
            screen.fill(light_blue)
        self.stimuli[self.selected].draw(screen)                                # Only the selected sequence, no cursor

        if self.event1 == False:                                                # Only happens on the first frame of phase 2
            refresh(screen)                                                     # Show the feedback screen BEFORE the pellet
            if self.is_probe:
                pellet(self.pellets)                                            # No sound on probes
            elif self.correct == 1:
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

        if self.is_probe:
            colors = ["NA"] * 7                                                 # No colors on shape trials
        else:
            colors = [self.color_A[0], self.color_A[1], self.color_A[2], self.color_B[0], self.color_B[1], self.color_B[2], self.color_dE]

        data = [monkey, version, today, now, self.testing_trial_number(), self.today_counts['trials'], self.blocks_completed + 1, self.trials_into_block + 1,
                self.trial_type(), self.probe_number, self.shape_pair,
                self.rule, self.config, loc["ABA"], loc["AAB"], loc["BAA"], loc[self.rule],
                self.chosen_sequence, self.chosen_sequence_num, self.chosen_location, self.correct, self.rt, self.cursor_xy[0], self.cursor_xy[1]] + colors + [self.pellets]

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
pellets_per_correct = params['pellets_per_correct']     # Pellets for a correct color trial AND for every shape probe

if rule not in foil_lookup:
    print("ERROR: RULE in parameters.txt is " + str(rule) + ". It must be \"ABA\", \"AAB\", or \"BAA\"")
    input("Press Enter to close...")
    sys.exit()

print("Monkey: " + monkey + "   Rule: " + rule + "   ITI: " + str(ITI) + "   Timeout: " + str(time_out))


"""SET UP THE TEST: WHERE DID THIS MONKEY LEAVE OFF? -----------------------------------------------------------------"""
blocks_completed = read_number(testing_blocks_file)
probes_completed = read_number(probes_completed_file)
probe_order = shuffle_probe_order_if_new(read_probe_order(), blocks_completed, probes_completed)
probe_configs = build_probe_configs(probe_order)

# How many trials into the current block did the monkey get last time? (from the old data files)
trials_done = count_testing_trials_done()
if trials_done >= (blocks_completed + 1) * block_length:
    # The program closed right after finishing a block, before it could save testing_blocks.txt
    print("NOTE: data files show " + str(trials_done) + " testing trials, fixing " + testing_blocks_file)
    blocks_completed = trials_done // block_length
    write_number(testing_blocks_file, blocks_completed)
trials_into_block = trials_done - blocks_completed * block_length
if trials_into_block < 0:
    print("WARNING: data files show fewer trials than " + testing_blocks_file + ". Starting a fresh block")
    trials_into_block = 0
if probes_completed > blocks_completed + 1 or probes_completed < blocks_completed:
    print("WARNING: " + probes_completed_file + " (" + str(probes_completed) + ") does not match "
          + testing_blocks_file + " (" + str(blocks_completed) + "). There should be exactly 1 probe per block")

if probes_completed >= total_probes and trials_into_block == 0:
    all_done_popup()                                    # Already finished: nothing left to run


"""CREATE THE DATA FILE-------------------------------------------------------------------------------------------"""
data_file = makeFileName(data_file_task)
if not os.path.isfile(data_file):                       # Only write the header once (if the task is restarted today, keep adding to the same file)
    writeLn(data_file, ['monkey', 'version', 'date', 'time', 'testing_trial_number', 'trial_number_today', 'testing_block', 'trial_within_block',
                        'trial_type', 'probe_trial_number', 'shape_pair',
                        'rule', 'position_config', 'ABA_location', 'AAB_location', 'BAA_location', 'correct_location',
                        'chosen_sequence', 'chosen_sequence_num', 'chosen_location', 'correct', 'rt', 'cursor_x', 'cursor_y',
                        'A_red', 'A_green', 'A_blue', 'B_red', 'B_green', 'B_blue', 'color_deltaE_min', 'pellets'])


# START THE CLOCK
clock = pygame.time.Clock()

# CREATE THE TASK WINDOW
screen = setScreen(full_screen)
pygame.display.set_caption("ABA Task - Color / Shape Test v1")
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
