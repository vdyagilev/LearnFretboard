# command-line game for generating a random starting note on fretboard and a mode
from helpers import screen_clear
from constants import MODE_NAMES, NOTE_POS, STRING_NAMES
import random

while True:
    # randomly select note on fretboard
    chosen_string = random.randint(0, 5)
    chosen_string_name = STRING_NAMES[chosen_string]
    chosen_fret = random.randint(0, 12)
    chosen_note = NOTE_POS[chosen_string][chosen_fret]

    # randomly select mode
    chosen_mode = random.randint(0, 6)
    chosen_mode_name = MODE_NAMES[chosen_mode]

    # randomly select horizontal direction to play
    chosen_direction = random.choice(["left", "right"])

    # print to use
    screen_clear()
    print("My dude, please play: \n")
    print(f"{chosen_note} {chosen_mode_name.capitalize()} starting from:\n    the {chosen_string_name} string on the {chosen_fret} fret")
    print(f"        to the {chosen_direction}")

    # wait for next
    input("\npress enter to continue")

