# generate random chord progression in a random key, then quiz user it
from helpers import make_overtoned_sounds_from_freq, play_sounds_together
from constants import DORIAN_CHORDS, LOCRIAN_CHORDS, LYDIAN_CHORDS, MAJOR_CHORDS, MINOR_CHORDS, MIXOLYDIAN_CHORDS, NOTE_FREQ, NOTE_NAMES, NOTE_POS, PHRYGIAN_CHORDS, SAMPLE_RATE
from constants import _MAJ, _MIN, _DIM 
import random
import pygame
import time

MODE_NAMES = ['major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'minor', 'locrian']

def play_chord(fun_freq, chord_version, millisecs, seed=None, n_overtone=3):
    # chord based on just intonation
    min_second = fun_freq*(16/15)
    maj_second = fun_freq*(9/8)
    min_third = fun_freq*(6/5)
    maj_third = fun_freq*(5/4)
    perf_fourth = fun_freq*(4/3)
    tritone = fun_freq*(45/32)
    perf_fifth = fun_freq*(3/2)
    minor_sixth = fun_freq*(8/5)
    major_sixth = fun_freq*(5/3)
    minor_seventh = fun_freq*(9/5)
    major_seventh = fun_freq*(15/8)
    octave = fun_freq*(2/1)
    
    if chord_version == _MAJ:
        un, deux, trois = fun_freq, maj_third, perf_fifth 

    elif chord_version == _MIN:
        un, deux, trois = fun_freq, min_third, perf_fifth 

    elif chord_version == _DIM:
        un, deux, trois = fun_freq, maj_third, tritone
    
    else:
        print("UNACCEPTED MODE: ", chord_version)
        exit(1)

    tones = [un, deux, trois]

    # add octaves randomly
    random.seed(a=seed)
    for i, tone in enumerate(tones):
        rand = random.randint(0, 100)
        if rand < 25:
            tones[i] = tone * (2/1) # up an octave
        elif rand < 35:
            tones[i] = tone * (4/1) # up two octave
        elif rand < 50:
            tones[i] = tone * (0.5/1) # down one octave
        elif rand < 60:
            tones[i] = tone * (0.25/1) # down two octave

    sounds = [ make_overtoned_sounds_from_freq(f, n=n_overtone) for f in tones ]
    sounds = sum(sounds, []) # collapse nested lists
    play_sounds_together(sounds, millisecs)

if __name__ == '__main__':
    # init pygame
    pygame.init()
    # init sound library
    pygame.mixer.init(SAMPLE_RATE,-16,2,512)

    while True:
        chosen_key = random.choice(NOTE_NAMES)
        chosen_mode = random.randint(0, 6)

        num_chords = random.randint(10, 14)

        mode_mapping = [MAJOR_CHORDS, DORIAN_CHORDS, PHRYGIAN_CHORDS, LYDIAN_CHORDS, MIXOLYDIAN_CHORDS, MINOR_CHORDS,LOCRIAN_CHORDS]

        # map each chord version from the mode to its index in a typle (index, chord_vers)
        chosen_chords = [ (i, vers) for i, vers in enumerate(mode_mapping[chosen_mode]) ]

        # add in octave
        chosen_chords.append(chosen_chords[0])

        # # draw # num_chords randomly-samples from chosen_chords and replace them
        # _weights = [0.5, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1] # weight root key most
        # _chords = random.choices(chosen_chords, weights= _weights, k=num_chords)
        # chosen_chords = _chords

        # play them
        print("\nWhat key and mode is this chord progression in?")

        for chord_idx, chord_vers in chosen_chords:
            # get fundemental frequency of chosen key note
            root_string = random.choice([0, 1, 2])
            fret_idx = (NOTE_POS[root_string].index(chosen_key) + chord_idx) % 13

            fun_freq = NOTE_FREQ[root_string][fret_idx]

            # determine version of chord from mode
            play_len, play_times = random.choice([(500, 1)])

            seed = random.randint(0, 10000)
            for _ in range(play_times):
                play_chord(fun_freq, chord_vers, play_len, seed=seed)
                time.sleep(random.randint(100, 250)/1000)

        # quiz user
        print("(Enter mode from ['major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'minor', 'locrian'])")
        mode_inputted = input("mode: ")

        print(f"(Enter key from {NOTE_NAMES}")
        key_inputted = input("key: ")

        # respond 
        if mode_inputted == chosen_mode or mode_inputted == MODE_NAMES[chosen_mode]:
            print("CORRECT MODE!")
        else:
            print("INCORRECT MODE!")

        print(f"The mode was {MODE_NAMES[chosen_mode]}")

        # respond 
        if key_inputted == chosen_key or key_inputted in chosen_key.split("/"):
            print("CORRECT KEY!")
        else:
            print("INCORRECT KEY!")

        print(f"The key was {chosen_key}")

        print("**********************************************\n\n\n")
            
            