import random
import time

from constants import MODE_NAMES, NOTE_NAMES
from helpers import calc_num_semitones, screen_clear

while True:
    screen_clear()

    pitch = random.choice(NOTE_NAMES)
    pitch_name = pitch
    if "/" in pitch:
        pitch_name = pitch.split("/")[random.randint(0, 1)].capitalize()

    mode = random.choice(MODE_NAMES)
    guess = input(f'What is the Major Scale for {pitch_name} {mode.capitalize()}?\n')

    mode_idx = MODE_NAMES.index(mode)

    def shift_pitch(pitch, half_steps):
        if (half_steps) < 0:
            half_steps = 12 + half_steps

        # return pitch half_steps above pitch
        pitch_idx = NOTE_NAMES.index(pitch)

        step_left = half_steps
        while step_left > 0:
            pitch_idx += 1
            step_left -= 1

        return NOTE_NAMES[pitch_idx % len(NOTE_NAMES)]
    
    major_mode = 0
    shift_amount = calc_num_semitones(mode_idx, major_mode)

    answer_pitch = shift_pitch(pitch, -shift_amount)

    if (guess.lower() in answer_pitch.lower()):
        print("Correct!")
        time.sleep(1)
    else:
        print(f"Incorrect! It is {answer_pitch.capitalize()}")
        time.sleep(1)
    