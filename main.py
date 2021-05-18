import pygame
import sys
import random
import pickle


# screen dimensions
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1000

# default colours 
WHITE = (255,255,255)
DARK_GREY = (100,100,100)
LIGHT_GREY = (170,170,170)

# colours for fretboard buttons
COLORS = {
    "A": (226, 50, 51),
    "As/Bf": DARK_GREY,
    "B": (114, 43, 235),
    "C": (198, 247, 253),
    "Cs/Df": DARK_GREY, 
    "D": (69, 216, 85),
    "Ds/Ef": DARK_GREY,
    "E": (250, 135, 31),
    "F": (61, 60, 60),
    "Fs/Gf": DARK_GREY, 
    "G": (109, 65, 26),
    "Gs/Af": DARK_GREY,
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
NOTE_RADIUS = 20
BUTTON_RADIUS = 28

# local file to store history
SAVED_DATA_FILE = "saved_data.pickle"

# number of seconds to display correct answer
DISPLAY_ANSWER_TIME = 1

################################################################################################

class Note:
    """Represents a single note and its game properties on the fretboard"""
    def __init__(self, name: str, string_idx: int, fret_idx: int):
        # basic details
        self.name = name
        self.string_idx = string_idx
        self.fret_idx = fret_idx

        # prediction accuracy
        self.num_correct = 0
        self.num_wrong = 0

        # pygame display details
        self.color = COLORS[name]
        # calculate (x, y) of note on fretboard image
        left_edge = 150
        bottom_edge = 658
        self.screen_pos = (left_edge + (fret_idx * 106), bottom_edge - (string_idx * 108))

    def get_accuracy(self) -> float:
        """Returns the prediction accuracy"""
        try:
            return self.num_correct / self.num_wrong
            
        except ZeroDivisionError:
            if self.num_correct == 0:
                return 0.0
            if self.num_wrong == 0:
                return 1.0

    def __str__(self):
        return f'({self.name}) string: {self.string_idx} fret: {self.fret_idx} screen_coord: {self.screen_pos}'

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


def choose_note(curr_stats, hist_stats):
    """Returns a note for user to predict. Returns in-progress note or random note from the 3 with lowest accuracy"""
    total_pred = curr_stats["num_correct"] + curr_stats["num_wrong"]

    # user has yet to predict last given note
    if len(curr_stats["note_history"]) > total_pred:
        return curr_stats["note_history"][-1]
    
    # return a random note with probability distribution of the inverse of their prediction accuracy (prefer inaccurate notes)
    prob_dist = []
    for note in hist_stats:
        try:
            prob_dist.append(1/note.get_accuracy())

        except ZeroDivisionError:
            prob_dist.append(1)

    return random.choices(hist_stats, prob_dist, k=1)[0]
    
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

    # init pygame related constants

    # default font
    TITLE_FONT = pygame.font.SysFont('Corbel', 42)
    BUTTON_FONT = pygame.font.SysFont('Corbel', 21)

    # load fretboard skeleton image
    fretboard_image = pygame.image.load("fretboard-skeleton.jpg")

    # init screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # rendering a text written in
    # this font
    title = TITLE_FONT.render('Learn Fretboard Notes', True, DARK_GREY)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # GAME LOOP
    curr_stats = {"num_correct": 0, "num_wrong": 0, "note_history": []} # keep track of curr round metrics
    while True:

        # fill screen with background colour
        screen.fill(LIGHT_GREY)

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

        # choose note for user to predict
        predict_note = choose_note(curr_stats, saved_data)
        print(predict_note)

        # if we get a new note, record it into curr_stats note history
        if len(curr_stats["note_history"]) == curr_stats["num_correct"] + curr_stats["num_wrong"]:
            curr_stats["note_history"].append(predict_note)

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

                if butt_press_name != "":
                    # record correct guess, reveal, and continue
                    if butt_press_name == predict_note.name:
                        # record current game stats
                        curr_stats["num_correct"] += 1
                        # record saved file data
                        for saved_note in saved_data:
                            if saved_note.name == predict_note.name and saved_note.string_idx == predict_note.string_idx and saved_note.fret_idx == predict_note.fret_idx:
                                saved_note.num_correct += 1

                        # reveal, colour circle and draw text
                        pygame.draw.circle(screen, predict_note.color, predict_note.screen_pos, NOTE_RADIUS)
                        if "/" in predict_note.name:
                            screen.blit(BUTTON_FONT.render(predict_note.name, True, WHITE), (predict_note.screen_pos[0]-18, predict_note.screen_pos[1]-7))
                        else:
                            screen.blit(BUTTON_FONT.render(predict_note.name, True, WHITE), (predict_note.screen_pos[0]-4, predict_note.screen_pos[1]-7))

                        pygame.display.update()
                        pygame.time.delay(1000 * DISPLAY_ANSWER_TIME)

                    # record incorrect guess, reveal, and continue
                    else:
                        curr_stats["num_wrong"] += 1
                        for saved_note in saved_data:
                            if saved_note.name == predict_note.name and saved_note.string_idx == predict_note.string_idx and saved_note.fret_idx == predict_note.fret_idx:
                                saved_note.num_wrong += 1

                    # save to file
                    save_data(saved_data)

                    # print accuracies of all notes
                    sorted_notes = sorted(saved_data, key=lambda n: n.get_accuracy())
                    print("\nHow I'm Doing")
                    for note in sorted_notes:
                        print(f'{note.name} sf: ({note.string_idx}, {note.fret_idx}) accur: {note.get_accuracy()}')
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
                else:
                    pass


        # updates the frames of the game
        pygame.display.update()
