import numpy as np
from constants import *
import pickle
import pygame
import datetime as dt

def load_data(filename: str) -> list:
    """Load data of note accuracies and such from pickled file"""
    with open(f'{SAVED_DATA_DIR}/{filename}', 'rb') as handle: 
        return pickle.load(handle)

def save_data(data: list, filename: str):
    """Save data of note accuracies and such from pickled file"""
    with open(f'{SAVED_DATA_DIR}/{filename}', 'wb') as handle:
        pickle.dump(data, handle)

def zero_one_norm(xi, max_i, min_i):
    if max_i == min_i:
        return xi
        
    return (xi - min_i) / (max_i - min_i)

# return data list with outliers removed. m controls removal pressure.
def reject_outliers(data, m=6.):
            d = np.abs(data - np.median(data))
            mdev = np.median(d)
            s = d / (mdev if mdev else 1.)
            return data[s < m].tolist()

def notes_equal(x, y) -> bool:
    """Returns True if Note x and Note y share same position on the fretboard"""
    return x.name == y.name and x.string_idx == y.string_idx and x.fret_idx == y.fret_idx

def intervals_equal(x, y) -> bool:
    """Returns True if Interval x and Interval y have the same notes"""
    return notes_equal(x.note_a, y.note_a) and notes_equal(x.note_b, y.note_b)

def string_idx_to_letter(idx: int) -> str:
    """Returns the letter of the idx of the string"""
    strings = ['E', 'A', 'D', 'G', 'B', 'E']
    return strings[idx]

def get_interval_name(note_a, note_b) -> str:
    # if same note
    if note_a.name == note_b.name:
        if NOTE_FREQ[note_a.string_idx][note_a.fret_idx] != NOTE_FREQ[note_b.string_idx][note_b.fret_idx]:
            return "Octave"
        else:
            return "Unison"
    
    # else find how many half steps from note_a to note_b if note_b is higher in pitch (irregardless of its real pitch)
    num_half_steps = 1
    note_a_idx = NOTE_NAMES.index(note_a.name)
    note_names = NOTE_NAMES + NOTE_NAMES + NOTE_NAMES # used to easily traverse upwards without fear of oob
    note_above_note_a = note_names[note_a_idx+num_half_steps]
    while note_b.name != note_above_note_a:
        # incremement upwards to the next halfstep
        num_half_steps += 1
        note_above_note_a = note_names[note_a_idx+num_half_steps]
    
    # num_half_steps is the distance between the note_a to note_b when note_b is higher in pitch
    return INTERVAL_NAMES[num_half_steps]

def calc_prob_dist_guessmaker(guessmaker_list, init_weight=100):
    # return a random note with probability distribution of the inverse of their prediction accuracy (prefer inaccurate notes)
    # and their avg time 

    prob_dist = []
    for gm in guessmaker_list:
        # before any guesses (initialized)
        if len(gm.guesses) == 0:
            prob_dist.append(2*init_weight)

        else:
            # inverse of guess acc ([0,1]) + note guess time in seconds
            if gm.get_accuracy() == 0:
                a = init_weight
            else:
                a = (1/gm.get_accuracy())

            b = gm.get_avg_guess_time()
            prob_dist.append( a + b)
    

    # normalize prob dist between 0 and 1
    max_i, min_i = max(prob_dist), min(prob_dist)
    prob_dist = [zero_one_norm(x, max_i, min_i) for x in prob_dist]

    return prob_dist

def combine_colors(a, b):
    # color_a, color_b: (float64, float54, float64)  RGB
    # example: red = (226, 50, 51)
    return (a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2

def simple_linspace(lower, upper, length):
    """linear interpolation between two points lower and upper. length amount of points returned. Includes right endpoint"""
    return [lower + x*(upper-lower)/(length-1) for x in range(length)]


def get_note_pos(notes_list, pos_list, note):
    idx = 0
    for n in notes_list:
        if notes_equal(n, note):
            return pos_list[idx]
        idx += 1
    return




def make_pygame_sound_from_freq(freq):
    arr = np.array([4096 * np.sin(2.0 * np.pi * freq * x / SAMPLE_RATE) for x in range(0, SAMPLE_RATE)]).astype(np.int16)
    arr2 = np.c_[arr,arr]
    sound = pygame.sndarray.make_sound(arr2)
    return sound

def play_notes_harmonic(note_a, note_b, millisecs):
    sound_a = make_pygame_sound_from_freq(note_a.frequency)
    sound_b = make_pygame_sound_from_freq(note_b.frequency)

    sound_a.play(-1)
    sound_b.play(-1)

    pygame.time.delay(millisecs)

    sound_a.stop()
    sound_b.stop()

def hour_now() -> int:
    return dt.datetime.today().hour