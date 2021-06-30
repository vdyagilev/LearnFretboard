from numpy.lib.polynomial import _poly_dispatcher
import pygame
import sys
import random
import pickle
import numpy
import time


# screen dimensions
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1000

# default colours 
WHITE = (255,255,255)
DARK_GREY = ( 111, 111, 111)
LIGHT_GREY = (170,170,170)
VERY_DARK_GREY = (13, 13, 13)
SUCCESS_GREEN = (0, 48, 18)
FAILURE_RED = (71, 0, 15)
BEEKEEPER = (246, 229, 141)
SPICED_NECTARINE = (255, 190, 118)

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

# playing tone
NOTE_FREQ = {
    0: [82.41, 87.31, 92.50, 98.00, 103.83, 110.00, 116.54, 123.47, 130.81, 138.59, 146.83, 155.56, 164.81],
    1: [110.00, 116.54, 123.47, 130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.00],
    2: [146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.00, 233.08, 246.94, 261.63, 277.18, 293.66],
    3: [196.00, 207.65, 220.00, 233.08, 246.94, 261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00],
    4: [246.94, 261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88],
    5: [329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88, 523.25, 554.37, 587.33, 622.25, 659.26],
}
SAMPLE_RATE = 44100

NOTE_RADIUS = 20
BUTTON_RADIUS = 28

# local file to store history
SAVED_DATA_FILE = "saved_data.pickle"

# number of seconds to display correct answer
DISPLAY_ANSWER_TIME = 2 # seconds

################################################################################################

class Guess:
    def __init__(self, real: str, guessed: str, time: int):
        self.real = real
        self.guessed = guessed
        self.time = time
        self.was_correct = self.real == self.guessed

class Note:
    """Represents a single note and its game properties on the fretboard"""
    def __init__(self, name: str, string_idx: int, fret_idx: int, num_correct=0, total_guesses=0, times=[]):
        # basic details
        self.name = name
        self.string_idx = string_idx
        self.fret_idx = fret_idx

        # pygame display details
        self.color = COLORS[name]

        # calculate (x, y) of note on fretboard image
        left_edge = 150
        bottom_edge = 658
        self.screen_pos = (left_edge + (fret_idx * 106), bottom_edge - (string_idx * 108))

        # sound frequency
        self.frequency = NOTE_FREQ[string_idx][fret_idx]

        # for average guess time
        self.GUESS_CACHE_LEN = 100 # keep the times for only # of last guesses for averaging
        self.NUM_GUESSES_TO_USE = 4
        self.guesses = []

    def get_accuracy(self) -> float:
        """Returns the prediction accuracy"""
        try:
            num_correct = 0
            total_guesses = 0
            for guess in self.guesses[-self.NUM_GUESSES_TO_USE:]:
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
        for guess in self.guesses[-self.NUM_GUESSES_TO_USE:]:
            total_time += guess.time

        avg_mls = total_time / self.NUM_GUESSES_TO_USE

        # convert to secs
        return 1000.0 * avg_mls 

    def add_guess(self, guess: Guess):
        # trim self.guesses to avoid too much data
        self.guesses = self.guesses[-self.GUESS_CACHE_LEN:]
        self.guesses.append(guess)

    def play_sound(self):
        arr = numpy.array([4096 * numpy.sin(2.0 * numpy.pi * self.frequency * x / SAMPLE_RATE) for x in range(0, SAMPLE_RATE)]).astype(numpy.int16)
        arr2 = numpy.c_[arr,arr]
        sound = pygame.sndarray.make_sound(arr2)
        sound.play(-1)
        pygame.time.delay(1000)
        sound.stop()

    def __str__(self):
        return f'({self.name}) string: {self.string_idx} fret: {self.fret_idx} screen_coord: {self.screen_pos} num_corr: {self.num_correct} total_guess: {self.total_guesses}'

def load_data() -> list:
    """Load data of note accuracies and such from pickled file"""
    with open(SAVED_DATA_FILE, 'rb') as handle:
        return pickle.load(handle)

def save_data(data: list):
    """Save data of note accuracies and such from pickled file"""
    with open(SAVED_DATA_FILE, 'wb') as handle:
        pickle.dump(data, handle)

def button_at_pos(coord: tuple) -> str:
    """Return which button is located at (x,y)=coord, or "" if none"""
    for i, note_name in enumerate(NOTE_NAMES):
        # check if y coord within button menu
        dist_between = 125
        height = 72
        if coord[1] > 876 and coord[1] < 924:
            if coord[0] > (i*dist_between)+height and coord[0] < (i*dist_between) + height+55:
                return note_name

    return ""


def zero_one_norm(xi, max_i, min_i):
    if max_i == min_i:
        return xi
        
    return (xi - min_i) / (max_i - min_i)

def choose_note(curr_stats, hist_stats):
    """Returns a note for user to predict. Returns in-progress note or random note from the 3 with lowest accuracy"""
    total_pred = curr_stats["num_correct"] + curr_stats["num_wrong"]

    # user has yet to predict last given note
    if len(curr_stats["note_history"]) > total_pred:
        return curr_stats["note_history"][-1]
    
    # return a random note with probability distribution of the inverse of their prediction accuracy (prefer inaccurate notes)
    # and their avg time 

    prob_dist = []
    for note in hist_stats:
        # before any guesses (initialized)
        if len(note.guesses) == 0:
            prob_dist.append(100)

        else:
            # inverse of note guess acc ([0,1]) + note guess time in seconds
            if note.get_accuracy() == 0:
                a = 100
            else:
                a = (1/note.get_accuracy())
            b = note.get_avg_guess_time()
            prob_dist.append( a + b)
    

    # normalize prob dist between 0 and 1
    max_i, min_i = max(prob_dist), min(prob_dist)
    prob_dist = [zero_one_norm(x, max_i, min_i) for x in prob_dist]

    print(f'\n {prob_dist} \n')

    return random.choices(hist_stats, prob_dist, k=1)[0]
    
def notes_equal(x, y) -> bool:
    """Returns True if Note x and Note y share same position on the fretboard"""
    return x.name == y.name and x.string_idx == y.string_idx and x.fret_idx == y.fret_idx

def string_idx_to_letter(idx: int) -> str:
    """Returns the letter of the idx of the string"""
    strings = ['E', 'A', 'D', 'G', 'B', 'E']
    return strings[idx]

def get_interval_name(last_note: Note, predict_note: Note) -> str:
    # if same note
    if last_note.name == predict_note.name:
        if NOTE_FREQ[last_note.string_idx][last_note.fret_idx] != NOTE_FREQ[predict_note.string_idx][predict_note.fret_idx]:
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
    first_idx = unique_freqs.index(last_note.frequency)
    second_idx = unique_freqs.index(predict_note.frequency)

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
    
    #print(f'note a: {last_note.name} note b: {predict_note.name} num_half_steps: {num_half_steps} interval_name: {interval_name}')
    return interval_name

        

# Run game
if __name__ == "__main__":
    try:
        # init saved data
        saved_data = load_data()

    except:
        # create new saved data dict containing a Note class instance for each note on the fretboard
        saved_data = []
        for string_idx, notes_lst in NOTE_POS.items():
            for fret_idx, note_name in enumerate(notes_lst):
                # create dict for each note on fretboard to keep track of correct and incorrect guesses
                saved_data.append(Note(note_name, string_idx, fret_idx))

        # save initial data list to file
        save_data(saved_data)

    # init pygame
    pygame.init()

    # init sound library
    pygame.mixer.init(SAMPLE_RATE,-16,2,512)

    # change window title
    pygame.display.set_caption('LearnFretboard')

    # init pygame related constants

    # default font
    TITLE_FONT = pygame.font.SysFont('Corbel', 42)
    BUTTON_FONT = pygame.font.SysFont('Corbel', 21)

    # load fretboard skeleton image
    fretboard_image = pygame.image.load("fretboard-skeleton.png")

    # init screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # rendering a text written in
    # this font
    title = TITLE_FONT.render('Learn Fretboard Notes', True, VERY_DARK_GREY)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # GAME LOOP
    curr_stats = {"num_correct": 0, "num_wrong": 0, "note_history": []} # keep track of curr round metrics
    last_note = None
    while True:

        # fill screen with background colour
        screen.fill(VERY_DARK_GREY)

        # draw freboard skeleton image
        screen.blit(fretboard_image, (0, 0))

        # draw title
        screen.blit(title, (630, 40))

        # draw num_correct and num_wrong this round
        num_correct_title = TITLE_FONT.render(f'Correct: {curr_stats["num_correct"]}', True, DARK_GREY)
        num_wrong_title = TITLE_FONT.render(f'Wrong: {curr_stats["num_wrong"]}', True, DARK_GREY)
        screen.blit(num_correct_title, (1150, 40))
        screen.blit(num_wrong_title, (1350, 40))

        # draw action buttons
        for i, note_name in enumerate(NOTE_NAMES):
            left_edge = 300
            right_edge = 1400
            x_step_size = (right_edge - left_edge) / len(NOTE_NAMES)
            # draw action button with label
            coord = (100 + i*(x_step_size+1.2*BUTTON_RADIUS), 900)
            pygame.draw.circle(screen, COLORS[note_name], coord, BUTTON_RADIUS)
            # render note names, sharps/flats are larger so shift them differently
            if "/" in note_name:
                screen.blit(BUTTON_FONT.render(note_name, True, WHITE), (coord[0]-18, coord[1]-7))
            else:
                screen.blit(BUTTON_FONT.render(note_name, True, WHITE), (coord[0]-5, coord[1]-7))

        # draw note to predict
        start_time = time.time()

        # choose note for user to predict
        predict_note = choose_note(curr_stats, saved_data)

        # if we get a new note, record it into curr_stats note history
        if len(curr_stats["note_history"]) == curr_stats["num_correct"] + curr_stats["num_wrong"]:
            curr_stats["note_history"].append(predict_note)

        # draw interval from last note, if last note exists and is not equal to this note
        if last_note and not notes_equal(last_note, predict_note):
            # draw line connecting them 
            pygame.draw.line(screen, BEEKEEPER, last_note.screen_pos, predict_note.screen_pos, width=8)
            # draw name of interval
            midp_x, midp_y = (last_note.screen_pos[0] + predict_note.screen_pos[0])/2, (last_note.screen_pos[1] + predict_note.screen_pos[1])/2
            
            # draw circle, and interval name on top

            # draw a grey note for user to predict
            pygame.draw.circle(screen, LIGHT_GREY, predict_note.screen_pos, NOTE_RADIUS)

            interval_name = get_interval_name(last_note, predict_note)
        
            screen.blit(BUTTON_FONT.render(interval_name, True, WHITE), (midp_x, midp_y-15))
        
        else:
            # draw a grey note for user to predict
            pygame.draw.circle(screen, LIGHT_GREY, predict_note.screen_pos, NOTE_RADIUS)
        


        # get user input and do actions

        # stores the (x,y) mouse coordinates in (x, y) tuple
        mouse = pygame.mouse.get_pos()

        # read user inputs
        for ev in pygame.event.get():

            # exit game and cleanup on quit
            if ev.type == pygame.QUIT:
                pygame.quit()
           
            # checks if a mouse is clicked
            if ev.type == pygame.MOUSEBUTTONDOWN:

                # get name of button pressed or ""
                butt_press_name = button_at_pos(mouse)
                
                if butt_press_name:

                    # record correct guess
                    if butt_press_name == predict_note.name:

                        # record current game stats
                        curr_stats["num_correct"] += 1

                        # record saved file data
                        for saved_note in saved_data:
                            if notes_equal(predict_note, saved_note):
                                # time to make choice from start
                                guess_time = time.time() - start_time 

                                # add guess to saved note class cached guess storage 
                                saved_note.add_guess(Guess(predict_note.name, butt_press_name, guess_time))

                        # create success text
                        success_text = TITLE_FONT.render('CORRECT', True, SUCCESS_GREEN)
                        loc_text = BUTTON_FONT.render(f'{string_idx_to_letter(predict_note.string_idx)} string {predict_note.fret_idx} fret', True, SUCCESS_GREEN)
                    
                    # record incorrect guess
                    else:
                        curr_stats["num_wrong"] += 1
                        for saved_note in saved_data:
                            if notes_equal(predict_note, saved_note):
                                # time to make choice from start
                                guess_time = time.time() - start_time 

                                # add guess to saved note class cached guess storage 
                                saved_note.add_guess(Guess(predict_note.name, butt_press_name, guess_time))
                        
                         # create failure text
                        success_text = TITLE_FONT.render('WRONG', True, FAILURE_RED)
                        loc_text = BUTTON_FONT.render(f'{string_idx_to_letter(predict_note.string_idx)} string {predict_note.fret_idx} fret', True, FAILURE_RED)

                    # reveal, colour circle and draw text
                    pygame.draw.circle(screen, predict_note.color, predict_note.screen_pos, NOTE_RADIUS)
                    if "/" in predict_note.name:
                        screen.blit(BUTTON_FONT.render(predict_note.name, True, WHITE), (predict_note.screen_pos[0]-18, predict_note.screen_pos[1]-7))
                    else:
                        screen.blit(BUTTON_FONT.render(predict_note.name, True, WHITE), (predict_note.screen_pos[0]-4, predict_note.screen_pos[1]-7))

                    # play tone
                    predict_note.play_sound()

                    # draw success or wrong text
                    screen.blit(success_text, (755, 715))
                    
                    # draw fret and string 
                    screen.blit(loc_text, (760, 750))

                    # update screen
                    pygame.display.update()
                    pygame.time.delay(1000 * DISPLAY_ANSWER_TIME)


                    # save to file
                    save_data(saved_data)

                    # print accuracies of all notes
                    sorted_notes = sorted(saved_data, key=lambda n: n.get_accuracy())

                    print("\nHow I'm Doing")
                    for note in sorted_notes:
                        print(f'{note.name} sf: ({note.string_idx}, {note.fret_idx}) accur: {note.get_accuracy()} avg time: {note.get_avg_guess_time()}' )
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

                    # save as temp variable, last_note
                    last_note = predict_note
                else:
                    pass


        # updates the frames of the game
        pygame.display.update()
