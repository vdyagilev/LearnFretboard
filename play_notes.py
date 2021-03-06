from structs import Guess, Note
from helpers import calc_prob_dist_guessmaker, get_interval_name, hour_now, is_light_color, load_data, notes_equal, save_data, simple_linspace, string_idx_to_letter, zero_one_norm, get_note_pos
import os
from constants import *

from numpy.lib.polynomial import _poly_dispatcher
import pygame
import sys
import random
import pickle
import numpy
import time
import matplotlib.pyplot as plt
import numpy as np


def get_all_notes_list():
    all_notes = []
    for string_idx, notes_lst in NOTE_POS.items():
        for fret_idx, note_name in enumerate(notes_lst): 
            all_notes.append(Note(note_name, string_idx, fret_idx))
    return all_notes

def button_at_pos(coord: tuple) -> str:
    """Return which button is located at (x,y)=coord, or "" if none"""
    num_cols = 12
    horiz_col_locs = [x for x in simple_linspace(side_padding, WINDOW_WIDTH-side_padding, num_cols)]
    butt_height = 40
    butt_width = 40
    for i, x in enumerate(horiz_col_locs):
        y = WINDOW_HEIGHT - menu_height/2
        # within vertical zone
        if coord[1] > y-butt_height/2 and coord[1] < y+butt_height/2:
            # within horiz zone
            if coord[0] > x-butt_width/2 and coord[0] < x+butt_width/2:
                # this idx contains the button. returns the note in idx
                return NOTE_NAMES[i]
    
    return ""


def choose_note(curr_stats, saved_data):
    """Returns a note for user to predict. Returns with probability based on past success"""
    total_pred = curr_stats["num_correct"] + curr_stats["num_wrong"]

    # user has yet to predict last given note
    if len(curr_stats["note_history"]) > total_pred:
        return curr_stats["note_history"][-1]
    
    # get zero-one normalized prob dist based on time and accuracy
    prob_dist = calc_prob_dist_guessmaker(saved_data)

    # add small number to ensure zero one is not zero anymore
    SMALL_NUM = (1/78)/5
    prob_dist = [x + SMALL_NUM for x in prob_dist]

    if RANDOM_NOT_DYNAMIC_PICKING:
        return random.choice(saved_data)

    return random.choices(saved_data, prob_dist, k=1)[0]
        

# Run game
if __name__ == "__main__":
    # Create directories if not yet made
    if not os.path.exists(SAVED_DATA_DIR):
        os.makedirs(SAVED_DATA_DIR)
        
    try:
        # init saved data
        saved_data = load_data(SAVED_NOTES_FILE)

    except:
        # create new saved data dict containing a Note class instance for each note on the fretboard
        saved_data = []
        for string_idx, notes_lst in NOTE_POS.items():
            for fret_idx, note_name in enumerate(notes_lst):
                # create dict for each note on fretboard to keep track of correct and incorrect guesses
                saved_data.append(Note(note_name, string_idx, fret_idx))

        # save initial data list to file
        save_data(saved_data, SAVED_NOTES_FILE)

    ALL_NOTES = get_all_notes_list()

    # init pygame
    pygame.init()

    # init sound library
    pygame.mixer.init(SAMPLE_RATE,-16,2,512)

    # init wrong sound
    error_sound = pygame.mixer.Sound('error.ogg')

    # change window title
    pygame.display.set_caption('LearnFretboard')

    # init pygame related constants

     # default font
    TITLE_FONT = pygame.font.SysFont('Corbel', 48)
    BUTTON_FONT = pygame.font.SysFont('Corbel', 21)
    LABEL_FONT = pygame.font.SysFont('Corbel', 42)

    # load fretboard skeleton image
    fretboard_image = pygame.image.load("fretboard-skeleton.png")

    # init screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

    if DRAW_TITLE:
        # rendering a text written in
        # this font
        title = TITLE_FONT.render('Learn Fretboard Notes', True, (45, 52, 54))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # GAME LOOP
    curr_stats = {"num_correct": 0, "num_wrong": 0, "note_history": []} # keep track of curr round metrics
    last_note = None
    while True:
         # SETUP UI VARIABLES
        top_padding = (WINDOW_HEIGHT/18)
        side_padding = (WINDOW_WIDTH/12)
        fretboard_side_padding = (WINDOW_WIDTH / 25)
        menu_height = (1/5) * WINDOW_HEIGHT

        # fill screen with background colour
        screen.fill((223, 230, 233))
        pygame.draw.rect(screen, (99, 110, 114), (0, WINDOW_HEIGHT-menu_height, WINDOW_WIDTH, menu_height/10))
        pygame.draw.rect(screen, (45, 52, 54), (0, WINDOW_HEIGHT-menu_height, WINDOW_WIDTH, menu_height))


        # resize image dynamically
        fretboard_image = pygame.image.load("fretboard-skeleton.png")
        resize_height_ratio = WINDOW_HEIGHT / fretboard_image.get_height()
        resize_width_ratio = WINDOW_WIDTH / fretboard_image.get_width()

        fretboard_image_height, fretboard_image_width = int(min(resize_width_ratio * fretboard_image.get_height() -2* top_padding, int(WINDOW_HEIGHT*(4/5) -  1 * top_padding)))    , int(WINDOW_WIDTH -  1 * side_padding)
       
        fretboard_image = pygame.transform.scale(fretboard_image, (fretboard_image_width, fretboard_image_height))

        # draw freboard skeleton image
        fretboard_vert_padding = ((WINDOW_HEIGHT - menu_height)  - fretboard_image_height )/2
        fretboard_side_padding = (WINDOW_WIDTH- fretboard_image_width )/2
        screen.blit(fretboard_image, (fretboard_side_padding, fretboard_vert_padding)) 

     
        if DRAW_TITLE:
            # draw title
            # create array of columns (each column is a x  in evenly spaced columns)
            num_cols = 6
            horiz_col_locs = [x for x in simple_linspace(side_padding, WINDOW_WIDTH-side_padding, num_cols)]
            screen.blit(title, (horiz_col_locs[1] - 120, 40)) # draw in center col


            # draw num_correct and num_wrong this round
            num_correct_title = LABEL_FONT.render(f'Correct: {curr_stats["num_correct"]}', True, DARK_GREY)
            num_wrong_title = LABEL_FONT.render(f'Wrong: {curr_stats["num_wrong"]}', True, DARK_GREY)
            screen.blit(num_correct_title, (horiz_col_locs[3], 45))
            screen.blit(num_wrong_title, (horiz_col_locs[4], 45))

        # draw action buttons
        num_cols = 12
        horiz_col_locs = [x for x in simple_linspace(side_padding, WINDOW_WIDTH-side_padding, num_cols)]
        for i, note_name in enumerate(NOTE_NAMES):
            # draw action button with label
            coord = (horiz_col_locs[i], WINDOW_HEIGHT - menu_height/2)

            # draw colored circle for note
            pygame.draw.circle(screen, COLORS[note_name], coord, BUTTON_RADIUS)

            if is_light_color(COLORS[note_name]):
                text_color = VERY_DARK_GREY
            else:
                text_color = WHITE
            
            if not JUST_COLORS:

                # render note names, sharps/flats are larger so shift them differently
                if "/" in note_name:
                    screen.blit(BUTTON_FONT.render(note_name, True, text_color), (coord[0]-18, coord[1]-7))
                else:
                    screen.blit(BUTTON_FONT.render(note_name, True, text_color), (coord[0]-5, coord[1]-7))

        # draw note to predict
        start_time = time.time()

        # choose note for user to predict
        predict_note = choose_note(curr_stats, saved_data)

        # if we get a new note, record it into curr_stats note history
        if len(curr_stats["note_history"]) == curr_stats["num_correct"] + curr_stats["num_wrong"]:
            curr_stats["note_history"].append(predict_note)


        # DRAW NOTES

        # Get position of note a and b as (x, y)
        # generate all positions on the guitar fretboard as a 2D matrix of coordinates
        all_note_pos = []
        # calc bottom-left and top-right corners locations of fretboard image
        fret_half_len = (WINDOW_WIDTH/44)
        bl = (fretboard_side_padding+0.8*fret_half_len, WINDOW_HEIGHT-fretboard_vert_padding-menu_height) 
        tr = (WINDOW_WIDTH-fretboard_side_padding-1.7*fret_half_len, fretboard_vert_padding)
        num_frets, num_strs = 13, 6
        for y in simple_linspace(bl[1], tr[1], num_strs):
            for x in simple_linspace(bl[0], tr[0], num_frets):
            
                # just append (x, y) coord to a LIST of points
                all_note_pos.append( (x, y) ) 
    
        
        # draw note names
        def draw_note_name(note, random_sharp_flat: bool):
            note_pos = get_note_pos(ALL_NOTES, all_note_pos, note)
            x, y = note_pos

            # text color white if dark color and dark if light color
            if is_light_color(note.color):
                text_color = VERY_DARK_GREY
            else:
                text_color = WHITE

            if "/" in note.name:
                if random_sharp_flat:
                    both_note_names = note.name.split("/")

                    random.seed(len(curr_stats["note_history"]) + hour_now()) # always pick same note during frame refresh with seeding
                    picked_name = random.choice(both_note_names)
                    
                    screen.blit(BUTTON_FONT.render(picked_name, True, text_color), (x-8, y-7))

                else:
                    screen.blit(BUTTON_FONT.render(note.name, True, text_color), (x-18, y-7))
            else:
                screen.blit(BUTTON_FONT.render(note.name, True, text_color), (x-4, y-7))

        if last_note:
            last_note_pos  = get_note_pos(ALL_NOTES, all_note_pos, last_note)
        predict_note_pos  = get_note_pos(ALL_NOTES, all_note_pos, predict_note)

        # draw interval from last note, if last note exists and is not equal to this note
        if last_note and not notes_equal(last_note, predict_note):
            # draw the Interval connecting the notes
            pygame.draw.line(screen, LIGHT_GREY, last_note_pos, predict_note_pos, width=14)

            # draw highlight around predict_note
            x_a, y_a = predict_note_pos
            pygame.draw.circle(screen, (52,73,94), (x_a, y_a), NOTE_RADIUS+12)
            pygame.draw.circle(screen, (96,115,127), (x_a, y_a), NOTE_RADIUS+6)

            # draw notes
            pygame.draw.circle(screen, last_note.color, last_note_pos, NOTE_RADIUS)
            pygame.draw.circle(screen, (149,165,166), predict_note_pos, NOTE_RADIUS)

            if not JUST_COLORS:
                draw_note_name(last_note, random_sharp_flat=True)
        
        else:
            # draw highlight around predict_note
            x_a, y_a = predict_note_pos
            pygame.draw.circle(screen, (52,73,94), (x_a, y_a), NOTE_RADIUS+12)
            pygame.draw.circle(screen, (96,115,127), (x_a, y_a), NOTE_RADIUS+6)

            # draw a grey note for user to predict
            pygame.draw.circle(screen, (149,165,166), predict_note_pos, NOTE_RADIUS)
        


        # get user input and do actions

        # stores the (x,y) mouse coordinates in (x, y) tuple
        mouse = pygame.mouse.get_pos()

        # read user inputs
        for ev in pygame.event.get():

            # exit game and cleanup on quit
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # resize window
            if ev.type == pygame.VIDEORESIZE:
                surface = pygame.display.set_mode((ev.w, ev.h), pygame.RESIZABLE)

                # UPDATE WINDOW_HEIGHT AND WINDOW_WIDTH
                WINDOW_HEIGHT, WINDOW_WIDTH = ev.h, ev.w
                continue
           
            # checks if a mouse is clicked
            if ev.type == pygame.MOUSEBUTTONDOWN:

                # get name of button pressed or ""
                butt_press_name = button_at_pos(mouse)
                
                if butt_press_name:
                    # record correct/incorrect guess into GuessMaker
                    for saved_note in saved_data:
                        if notes_equal(predict_note, saved_note):
                            # time to make choice from start
                            guess_time = time.time() - start_time 

                            # add guess to saved note class cached guess storage 
                            saved_note.add_guess(Guess(predict_note.name, butt_press_name, guess_time))

                    # Generate unique graphics for Incorrect and Correct guesses and record into curr_stats

                    if butt_press_name == predict_note.name:

                        # record current game stats
                        curr_stats["num_correct"] += 1

                        # create success text
                        success_text = TITLE_FONT.render('CORRECT', True, SUCCESS_GREEN)
                        loc_text = BUTTON_FONT.render(f'{string_idx_to_letter(predict_note.string_idx)} string {predict_note.fret_idx} fret', True, SUCCESS_GREEN)
                    
                    else:
                        error_sound.play()

                        if NO_WRONG:
                            continue

                        curr_stats["num_wrong"] += 1

                         # create failure text
                        success_text = TITLE_FONT.render('WRONG', True, FAILURE_RED)
                        loc_text = BUTTON_FONT.render(f'{string_idx_to_letter(predict_note.string_idx)} string {predict_note.fret_idx} fret', True, FAILURE_RED)

                    # reveal predict note true color, colour circle and draw text
                    pygame.draw.circle(screen, predict_note.color, predict_note_pos, NOTE_RADIUS)
                    
                    if not JUST_COLORS:
                        # if note is a sharp/flat, 50% chance to draw either one of the two names 
                        draw_note_name(predict_note, random_sharp_flat=True)

                    # # draw the interval name on the midpoint of the line
                    # if last_note:
                    #     interval_name = get_interval_name(last_note, predict_note)
                    #     midp_x, midp_y = (last_note_pos[0] + predict_note_pos[0])/2, (last_note_pos[1] + predict_note_pos[1])/2
                    #     screen.blit(LABEL_FONT.render(interval_name, True, WHITE), (midp_x, midp_y-15))


                    
                    # update screen
                    pygame.display.update()
                
                    # play tone
                    min_play, max_play = 400, 900
                    random_play_len = lambda : DISPLAY_ANSWER_TIME *  random.randint(min_play, max_play)
                    play_len = random_play_len()
                    predict_note.play_overtoned_sound(play_len, n=5)

                    # # draw success or wrong text
                    # screen.blit(success_text, (WINDOW_WIDTH/2 - 55, WINDOW_HEIGHT - menu_height - (side_padding/2)))
                    # pygame.display.update()
                    

                    # save to file
                    save_data(saved_data, SAVED_NOTES_FILE)

                    # every 10x notes print and draw stats
                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    if len(curr_stats["note_history"]) % 10 == 0:    
                        # print accuracies of all notes
                        sorted_notes = saved_data

                        print("\nHow I'm Doing")
                        for note in sorted_notes:
                            print(f'{note.name} sf: ({note.string_idx}, {note.fret_idx}) accur: {note.get_accuracy()} avg time: {note.get_avg_guess_time()}' )
                        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

                        # draw how im doing as bar chart
                        plt.bar([f'{n.name} ({n.frequency})' for n in sorted_notes], calc_prob_dist_guessmaker(sorted_notes))
                        plt.title('Weights of Next Note Pick')
                        plt.xlabel('Note')
                        plt.xticks(fontsize=8, rotation=90)
                        plt.ylabel('Factor')
                        plt.savefig('next_note_prob.png', bbox_inches='tight')
                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    
                    # save last_note as temp variable
                    last_note = predict_note
                else:
                    pass


        # updates the frames of the game
        pygame.display.update()
