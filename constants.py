# screen dimensions
WINDOW_WIDTH =int(0.7* 1600)
WINDOW_HEIGHT =int(0.7* 1000)

# default colours 
WHITE = (255,255,255)
DARK_GREY = ( 111, 111, 111)
LIGHT_GREY = (170,170,170)
VERY_DARK_GREY = (13, 13, 13)
SUCCESS_GREEN = (0, 48, 18)
FAILURE_RED = (71, 0, 15)
BEEKEEPER = (246, 229, 141)
SPICED_NECTARINE = (255, 190, 118)
BUTTON_BLUE = (15,163,249)
BUTTON_BLUE_GREY = (114,181,220)
BGND_PURPLE = (162, 155, 254)

# colours for fretboard buttons
COLORS = {
    "A": (226, 50, 51),
    "As/Bf": (92, 163, 255),
    "B": (186, 37, 245),
    "C": (227, 227, 227),
    "Cs/Df": (198, 247, 253), 
    "D": (69, 216, 85),
    "Ds/Ef": (252, 230, 28),
    "E": (250, 135, 31),
    "F": (61, 60, 60),
    "Fs/Gf": (0, 2, 122),
    "G": (109, 65, 26),
    "Gs/Af": (150, 23, 36),
}

NOTE_NAMES = ["A", "As/Bf", "B", "C", "Cs/Df", "D", "Ds/Ef", "E", "F", "Fs/Gf", "G", "Gs/Af"]
NOTE_POS = {
    0: ["E", "F", "Fs/Gf", "G", "Gs/Af", "A", "As/Bf", "B", "C", "Cs/Df", "D", "Ds/Ef", "E"],
    1: ["A", "As/Bf", "B", "C", "Cs/Df", "D", "Ds/Ef", "E", "F", "Fs/Gf", "G", "Gs/Af", "A"],
    2: ["D", "Ds/Ef", "E", "F", "Fs/Gf", "G", "Gs/Af", "A", "As/Bf", "B", "C", "Cs/Df", "D"],
    3: ["G", "Gs/Af", "A", "As/Bf", "B", "C", "Cs/Df", "D", "Ds/Ef", "E", "F", "Fs/Gf", "G"],
    4: ["B", "C", "Cs/Df", "D", "Ds/Ef", "E", "F", "Fs/Gf", "G", "Gs/Af", "A", "As/Bf", "B"],
    5: ["E", "F", "Fs/Gf", "G", "Gs/Af", "A", "As/Bf", "B", "C", "Cs/Df", "D", "Ds/Ef", "E"],
}

INTERVAL_NAMES = ["Unison", "Minor 2nd", "Major 2nd", "Minor 3rd", "Major 3rd", "Perfect 4th", "Tritone", "Perfect 5th", "Minor 6th", "Major 6th", "Minor 7th", "Major 7th", "Octave"]
SHORT_INTERVAL_NAMES = ["U", "m2", "M2", 'm3', 'M3', 'P4', 'T', 'P5', 'm6', 'M6', 'm7', 'M7', 'O']


# chord progressions
_MAJ = "major"
_MIN = "minor"
_DIM = "dim"

MAJOR_CHORDS = [_MAJ, _MIN, _MIN, _MAJ, _MAJ, _MIN, _DIM]
MAJOR_SCALE = ['W', 'W', 'H', 'W', 'W', 'W', 'H']

# sequence dorian -> locrian mode chords by shifting major chords by one each time
DORIAN_CHORDS = MAJOR_CHORDS[1:] + MAJOR_CHORDS[:1]
DORIAN_SCALE = MAJOR_SCALE[1:] + MAJOR_SCALE[:1]

PHRYGIAN_CHORDS = MAJOR_CHORDS[2:] + MAJOR_CHORDS[:2]
PHRYGIAN_SCALE = MAJOR_SCALE[2:] + MAJOR_SCALE[:2]

LYDIAN_CHORDS = MAJOR_CHORDS[3:] + MAJOR_CHORDS[:3]
LYDIAN_SCALE = MAJOR_SCALE[3:] + MAJOR_SCALE[:3]

MIXOLYDIAN_CHORDS = MAJOR_CHORDS[4:] + MAJOR_CHORDS[:4]
MIXOLYDIAN_SCALE = MAJOR_SCALE[4:] + MAJOR_SCALE[:4]

MINOR_CHORDS = MAJOR_CHORDS[5:] + MAJOR_CHORDS[:5]
MINOR_SCALE = MAJOR_SCALE[5:] + MAJOR_SCALE[:5]

LOCRIAN_CHORDS = MAJOR_CHORDS[6:] + MAJOR_CHORDS[:6]
LOCRIAN_SCALE = MAJOR_SCALE[6:] + MAJOR_SCALE[:6]

# playing tone
NOTE_FREQ = {
    0: [82.41, 87.31, 92.50, 98.00, 103.83, 110.00, 116.54, 123.47, 130.81, 138.59, 146.83, 155.56, 164.81],
    1: [110.00, 116.54, 123.47, 130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.00],
    2: [146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.00, 233.08, 246.94, 261.63, 277.18, 293.66],
    3: [196.00, 207.65, 220.00, 233.08, 246.94, 261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00],
    4: [246.94, 261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88],
    5: [329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88, 523.25, 554.37, 587.33, 622.25, 659.26],
}
SORTED_NOTE_FREQ = sum([str_vls for str_vls in NOTE_FREQ.values()], []) # sum() flattens 
SAMPLE_RATE = 44100

NOTE_RADIUS = 20
BUTTON_RADIUS = 28

# local file to store history
SAVED_DATA_DIR = "./saved_data"
SAVED_NOTES_FILE = "saved_notes.pickle"
SAVED_INTERVALS_FILE = "saved_intervals.pickle"

# number of seconds to display correct answer
DISPLAY_ANSWER_TIME = 1# seconds

# GuessMaker
GUESS_CACHE_LEN = 10 # how many guesses stores in guessmaker cache
GUESS_OUTLIER_AVG = 3 # how many guesses are used to detect outlier entries 

# if true then notes and intervals are randomly chosen, if false then follows eq.
RANDOM_NOT_DYNAMIC_PICKING = False

# Only show Intervals with half-step distance less than 
MAX_INTERVAL_DISTANCE = 100
MAX_FRET_WIDTH = 5

# If NO_WRONG = True then your mistakes won't be registerd
NO_WRONG = True

# Plays harmonic intervals over melodic intervals probability
HARMONIC_INTERVAL_PROB = 0.5

# Shows only intervals listed here
ACTIVE_INTERVALS = INTERVAL_NAMES

# If False then will not draw title and score texts
DRAW_TITLE = False
