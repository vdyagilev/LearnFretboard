from constants import *
from helpers import get_interval_name, reject_outliers, notes_equal

import pygame
import numpy
import numpy as np


# A Guess is something that has a real string value and a users prediction of it, and the time it took.
class Guess:
    def __init__(self, real: str, guessed: str, time: int):
        self.real = real
        self.guessed = guessed
        self.time = time
        self.was_correct = (real == guessed)

# GuessMaker holds guesses and keeps track of their metrics
class GuessMaker:
    def __init__(self, max_len, avg_num):
        # store the guesses in a list
        self.guesses = []

        # total kept (useful for rejecting outliers)
        self.max_len = max_len 

        # num of last guesses used to filter out outliers 
        self.avg_num = avg_num 
        

    def add_guess(self, guess: Guess):
        # run a service function 
        self._update_guesses()

        # add to storage
        self.guesses.append(guess)

    def _update_guesses(self):
        # trim self.guesses to avoid too much data
        self.guesses = self.guesses[-self.max_len:]

        # remove time outliers
        guess_times = np.array([guess.time for guess in self.guesses])
        normal_guess_times = reject_outliers(guess_times)

        # keep only guesses without outlier values
        updated = list(filter(lambda g: g.time in normal_guess_times, self.guesses))
        self.guesses = updated

    def get_accuracy(self) -> float:
        """Returns the prediction accuracy"""
        try:
            num_correct = 0
            total_guesses = 0
            for guess in self.guesses[-self.avg_num:]:
                if guess.was_correct:
                    num_correct += 1

                total_guesses += 1

            return num_correct / total_guesses

        except:
            if num_correct == 0 or total_guesses == 0:
                return 0.0

    def get_avg_guess_time(self) -> float:
        # return the avg guess time for n_last guesses in seconds
        total_time = 0.0
        for guess in self.guesses[-self.avg_num:]:
            total_time += guess.time

        avg_mls = total_time / self.avg_num

        # convert to secs
        return 1000.0 * avg_mls 

class Note(GuessMaker):
    """Represents a single note and its game properties on the fretboard"""
    def __init__(self, name: str, string_idx: int, fret_idx: int):
        # init guessmaker
        GuessMaker.__init__(self, GUESS_CACHE_LEN, GUESS_OUTLIER_AVG)

        # basic details
        self.name = name
        self.string_idx = string_idx
        self.fret_idx = fret_idx

        # pygame display details
        self.color = COLORS[name]

        # sound frequency
        self.frequency = NOTE_FREQ[string_idx][fret_idx]


    def play_sound(self, millisecs):
        arr = numpy.array([4096 * numpy.sin(2.0 * numpy.pi * self.frequency * x / SAMPLE_RATE) for x in range(0, SAMPLE_RATE)]).astype(numpy.int16)
        arr2 = numpy.c_[arr,arr]
        sound = pygame.sndarray.make_sound(arr2)
        sound.play(-1)
        pygame.time.delay(millisecs)
        sound.stop()

    def __str__(self):
        return f'({self.name}) string: {self.string_idx} fret: {self.fret_idx}'


def get_all_notes_list():
    all_notes = []
    for string_idx, notes_lst in NOTE_POS.items():
        for fret_idx, note_name in enumerate(notes_lst): 
            all_notes.append(Note(note_name, string_idx, fret_idx))
    return all_notes

ALL_NOTES = get_all_notes_list()



class Interval(GuessMaker):
    """Represents an interval between Note a and Note b on the fretboard"""
    def __init__(self, note_a: Note, note_b: Note):
        # init guessmaker
        GuessMaker.__init__(self, GUESS_CACHE_LEN, GUESS_OUTLIER_AVG)
        
        # basic details
        self.note_a = note_a
        self.note_b = note_b
        

    def __str__(self):
        name = get_interval_name(self.note_a, self.note_b)
        return f'({name})\n    Note A: {str(self.note_a)}\n    Note B: {str(self.note_b)}'


    def get_full_name(self) -> str:
        return get_interval_name(self.note_a, self.note_b)

    def get_short_name(self) -> str:
        idx = INTERVAL_NAMES.index(self.get_full_name())
        return SHORT_INTERVAL_NAMES[idx]


    def get_distance(self) -> int:
        """Returns the number of half-steps between note_a to note_b upwards"""
        idx_a, idx_b  = -1, -1
        for i, note in enumerate(ALL_NOTES):
            if notes_equal(note, self.note_a):
                idx_a = i

            if idx_a != -1 and notes_equal(note, self.note_b):
                idx_b = i

        half_steps = abs(idx_b - idx_a)

        return half_steps
            