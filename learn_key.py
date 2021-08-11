# generate random chord progression in a random key, then quiz user it
from os import closerange
from helpers import get_freqs, make_overtoned_sounds_from_freq, next_note, play_sounds_together, screen_clear
from constants import DORIAN_CHORDS, DORIAN_SCALE, LOCRIAN_CHORDS, LOCRIAN_SCALE, LYDIAN_CHORDS, LYDIAN_SCALE, MAJOR_CHORDS, MAJOR_SCALE, MINOR_CHORDS, MINOR_SCALE, MIXOLYDIAN_CHORDS, MIXOLYDIAN_SCALE, NOTE_FREQ, NOTE_NAMES, NOTE_POS, PHRYGIAN_CHORDS, PHRYGIAN_SCALE, SAMPLE_RATE
from constants import _MAJ, _MIN, _DIM 
import random
import pygame
import time

MODE_NAMES = ['major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'minor', 'locrian']


def play_chord(fun_freq, chord_version, millisecs, seed=None, n_overtone=1, randomize=True):
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

        extras = []
        r = random.randint(0, 100)
        if r < 25:
            extras.append(minor_seventh)
        elif r < 50:
            extras.append(major_seventh)

    elif chord_version == _MIN:
        un, deux, trois = fun_freq, min_third, perf_fifth 

        extras = []
        r = random.randint(0, 100)
        if r < 25:
            extras.append(minor_seventh)
        elif r < 50:
            extras.append(major_sixth)

    elif chord_version == _DIM:
        un, deux, trois = fun_freq, min_third, tritone

        extras = []
        r = random.randint(0, 100)
        if r < 25:
            extras.append(minor_seventh)
        elif r < 50:
            extras.append(major_sixth)
    
    else:
        print("UNACCEPTED MODE: ", chord_version)
        exit(1)

    tones = [un, deux, trois, octave,] + extras


    if randomize:
        # add octaves randomly
        random.seed(a=seed)
        for i, tone in enumerate(tones):
            rand = random.randint(0, 100)
            if rand < 15:
                tones[i] = tone * (2/1) # up an octave
            elif rand < 30:
                tones[i] = tone * (0.5/1) # down one octave

            elif rand < 40:
                tones[i] = tone * (4/1) # up two octave
            elif rand < 50:
                tones[i] = tone * (0.25/1) # down two octave

    # remove too-high frequencies
    for i, tone in enumerate(tones):
        MAX_FREQ = 600
        MIN_FREQ = 50
        if tone > MAX_FREQ:
            # halve it
            tones[i] = tone / 2
        if tone < MIN_FREQ:
            # double it
            tones[i] = tone * 2

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

         # NO LOCRIAN
        while chosen_mode == 6:
            chosen_mode = random.randint(0, 6)
            

        num_random_chords = 14

        mode_mapping = [MAJOR_CHORDS, DORIAN_CHORDS, PHRYGIAN_CHORDS, LYDIAN_CHORDS, MIXOLYDIAN_CHORDS, MINOR_CHORDS,LOCRIAN_CHORDS]

        # map each chord version from the mode to its index in a typle (index, chord_vers)
        chosen_chords = [ (i, vers) for i, vers in enumerate(mode_mapping[chosen_mode]) ]

        # draw # num_chords randomly-samples from chosen_chords and replace them
        _weights = [0.4, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1] # weight root key most
        _random_chords = random.choices(chosen_chords, weights= _weights, k=num_random_chords)

        # add in root at end
        chosen_chords.append(chosen_chords[0])



        # play them
        print("\nWhat key and mode is this chord progression in?")
        

        def calc_num_semitones(chord_idx, chosen_mode):
            scale_mapping = [MAJOR_SCALE, DORIAN_SCALE, PHRYGIAN_SCALE, LYDIAN_SCALE, MIXOLYDIAN_SCALE, 
                            MINOR_SCALE, LOCRIAN_SCALE]
            scale = scale_mapping[chosen_mode]

            semitones = 0
            curr_scale_step = 0
            for step in scale:
                if curr_scale_step == chord_idx:
                    # count how many semitones from root of chosen mode to the chord at idx
                    # so we break when we get to its idx
                    break

                if step == "H":
                    semitones += 1
                elif step == "W":
                    semitones += 2
                else:
                    print(f'step is not H or W. step={step}')
                    exit(1)

                curr_scale_step += 1
            
            return semitones


        for chord_idx, chord_vers in chosen_chords:
            # get fundemental frequency of chosen key note
            num_semitones = calc_num_semitones(chord_idx, chosen_mode) # num semitones from root to chord_idx location on fretboard
            fun_freq = random.choice( get_freqs( next_note(chosen_key, num_semitones), strings=[3, 4] ) )

            # determine version of chord from mode
            play_len = random.randint(600, 800)

            seed = random.randint(0, 10000)
            play_chord(fun_freq, chord_vers, play_len, seed=seed)

        time.sleep(2)

        for chord_idx, chord_vers in _random_chords:
            # get fundemental frequency of chosen key note
            num_semitones = calc_num_semitones(chord_idx, chosen_mode) # num semitones from root to chord_idx location on fretboard
            fun_freq = random.choice( get_freqs( next_note(chosen_key, num_semitones), strings=[0, 1, 2, 3, 4, 5] ) )

            # determine version of chord from mode
            play_len = random.randint(450, 850)

            seed = random.randint(0, 10000)
            play_chord(fun_freq, chord_vers, play_len, seed=seed, randomize=True)

        time.sleep(2)
        chosen_chords.reverse()

        for chord_idx, chord_vers in chosen_chords:
            # get fundemental frequency of chosen key note
            num_semitones = calc_num_semitones(chord_idx, chosen_mode) # num semitones from root to chord_idx location on fretboard
            fun_freq = random.choice( get_freqs( next_note(chosen_key, num_semitones), strings=[3, 4] ) )

            # determine version of chord from mode
            play_len = random.randint(600, 800)

            seed = random.randint(0, 10000)
            play_chord(fun_freq, chord_vers, play_len, seed=seed)

        # quiz user
        print("(Enter mode from ['major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'minor', 'locrian'])")
        mode_inputted = input("mode: ")

        print(f"(Enter key from {NOTE_NAMES}")
        key_inputted = input("key: ")

        # respond 
        if mode_inputted == str(chosen_mode) or mode_inputted == MODE_NAMES[chosen_mode]:
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


            
        time.sleep(5)
        screen_clear()