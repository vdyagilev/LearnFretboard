import numpy as np
from constants import *
import pickle

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
    
    # get unique notes only, first sort by freq then find num_half_steps diff between a and b
    all_freqs = []
    for _, freqs in NOTE_FREQ.items():
        all_freqs += freqs
    sorted_freqs = sorted(all_freqs)

    unique_freqs = []
    for f in sorted_freqs:
            if f not in unique_freqs:
                unique_freqs.append(f)
    

    # find positions in absolute frequency list
    first_idx = unique_freqs.index(note_a.frequency)
    second_idx = unique_freqs.index(note_b.frequency)

    # get difference
    num_half_steps = second_idx - first_idx

    # if true then will return the interval(y, x) if freq(x) > freq(y), rather than interval(x, y) 

    # aka: if note x is higher than y in pitch then will return interval from y to x.
    # otherwise returns x to y without account to pitch
    USE_ABSOLUTE_INTERVAL = False

    if num_half_steps > 0 :
        # second pitch is higher than first
        interval_name = INTERVAL_NAMES[num_half_steps % 12]
    else:
        if USE_ABSOLUTE_INTERVAL:
            # second pitch is lower than first. invert the intervals
            idx = 12-(12-(abs(num_half_steps) % 12))
            interval_name = INTERVAL_NAMES[idx]
        else:
            interval_name = INTERVAL_NAMES[num_half_steps % 12]
    
    #print(f'note a: {note_a.name} note b: {note_b.name} num_half_steps: {num_half_steps} interval_name: {interval_name}')
    return interval_name

def calc_prob_dist_guessmaker(guessmaker_list):
    # return a random note with probability distribution of the inverse of their prediction accuracy (prefer inaccurate notes)
    # and their avg time 

    prob_dist = []
    for gm in guessmaker_list:
        # before any guesses (initialized)
        if len(gm.guesses) == 0:
            prob_dist.append(100)

        else:
            # inverse of guess acc ([0,1]) + note guess time in seconds
            if gm.get_accuracy() == 0:
                a = 100
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