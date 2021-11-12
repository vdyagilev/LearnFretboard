import random

from constants import MODE_NAMES, NOTE_NAMES

while True:
    key = random.choice(NOTE_NAMES)
    if "/" in key:
        key = key.split("/")[random.randint(0, 1)]

    mode = random.choice(MODE_NAMES)
   

    print(f'Play {key.capitalize()} {mode.capitalize()} :)')
    input()