from play_notes import get_interval_name
import os
from structs import Guess, Interval, Note
from helpers import calc_prob_dist_guessmaker, combine_colors, intervals_equal, load_data,get_note_pos, notes_equal, save_data, simple_linspace, string_idx_to_letter, zero_one_norm
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
import math
import random


def get_all_notes_list():
    all_notes = []
    for string_idx, notes_lst in NOTE_POS.items():
        for fret_idx, note_name in enumerate(notes_lst): 
            all_notes.append(Note(note_name, string_idx, fret_idx))
    return all_notes

def button_at_pos(coord: tuple) -> str:
    """Return which button is located at (x,y)=coord, or "" if none"""
    num_cols = 13
    horiz_col_locs = [x for x in simple_linspace(side_padding, WINDOW_WIDTH-side_padding, num_cols)]
    butt_height = 40
    butt_width = 40
    for i, x in enumerate(horiz_col_locs):
        y = WINDOW_HEIGHT - menu_height/2
        # within vertical zone
        if coord[1] > y-butt_height/2 and coord[1] < y+butt_height/2:
            # within horiz zone
            if coord[0] > x-butt_width/2 and coord[0] < x+butt_width/2:
                # this idx contains the button. returns the full name of the interval in idx position
                return INTERVAL_NAMES[i]
    
    return ""


def choose_interval(curr_stats, hist_stats):
    """Returns an interval for user to predict. Returns with probability based on past success"""
    total_pred = curr_stats["num_correct"] + curr_stats["num_wrong"]

    # user has yet to predict last given note
    if len(curr_stats["interval_history"]) > total_pred:
        return curr_stats["interval_history"][-1]
    
    # get zero-one normalized prob dist based on time and accuracy
    prob_dist = calc_prob_dist_guessmaker(hist_stats)

    # add small number to ensure zero one is not zero anymore
    SMALL_NUM = (1/6084) # there are 6084 unique intervals

    prob_dist = [x + SMALL_NUM for x in prob_dist]

    if RANDOM_NOT_DYNAMIC_PICKING:
        return random.choice(hist_stats)

    return random.choices(hist_stats, prob_dist, k=1)[0]

# draw note names
def draw_note_name(note):
    note_pos = get_note_pos(ALL_NOTES, all_note_pos, note)
    x, y = note_pos
    if "/" in note.name:
        screen.blit(BUTTON_FONT.render(note.name, True, WHITE), (x-18, y-7))
    else:
        screen.blit(BUTTON_FONT.render(note.name, True, WHITE), (x-4, y-7))


# Run game
if __name__ == "__main__":
    if not os.path.exists(SAVED_DATA_DIR):
        os.makedirs(SAVED_DATA_DIR)

    try:
        # init saved data
        saved_data = load_data(SAVED_INTERVALS_FILE)

    except:
        # create new saved data dict containing an Interval class instance for each possible interval on the fretboard (first octave part only)
        saved_data = []
        count = 0
        # iterate thru every pair of notes
        for string_idx_a, notes_lst_a in NOTE_POS.items():
                for fret_idx_a, note_name_a in enumerate(notes_lst_a):
                    for string_idx_b, notes_lst_b in NOTE_POS.items():
                        for fret_idx_b, note_name_b in enumerate(notes_lst_b):
                            # init the two Note classes
                            note_a = Note(note_name_a, string_idx_a, fret_idx_a)
                            note_b = Note(note_name_b, string_idx_b, fret_idx_b)

                            # init the Interval class joining them
                            interval = Interval(note_a, note_b)
                    
                            saved_data.append(interval)

        
        # save initial data list to file
        save_data(saved_data, SAVED_INTERVALS_FILE)

    # used to calculate stuff
    ALL_NOTES = get_all_notes_list()

    # init pygame
    pygame.init()

    # init sound library
    pygame.mixer.init(SAMPLE_RATE,-16,2,512)

    # change window title
    pygame.display.set_caption('LearnFretboard')

    # init pygame related constants

    # default font
    TITLE_FONT = pygame.font.SysFont('Corbel', 48)
    BUTTON_FONT = pygame.font.SysFont('Corbel', 21)
    LABEL_FONT = pygame.font.SysFont('Corbel', 42)

    # init screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

    # rendering a text written in
    # this font
    title = TITLE_FONT.render('Learn Fretboard Intervals', True, (45, 52, 54))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    

    # GAME LOOP
    curr_stats = {"num_correct": 0, "num_wrong": 0, "interval_history": []} # keep track of curr round metrics
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
        num_cols = 13
        horiz_col_locs = [x for x in simple_linspace(side_padding, WINDOW_WIDTH-side_padding, num_cols)]
        for i, interval_name in enumerate(INTERVAL_NAMES):
            # draw action button with label
            coord = (horiz_col_locs[i], WINDOW_HEIGHT - menu_height/2)

            # even buttons slightly darker bgnd
            if i % 2 == 0:
                bngd_color = BUTTON_BLUE
            else:
                bngd_color = BUTTON_BLUE_GREY

            pygame.draw.circle(screen, bngd_color, coord, BUTTON_RADIUS)

            # get short interval name ex. (m3)
            short_interval_name = SHORT_INTERVAL_NAMES[i]
            if len(short_interval_name) != 1:
                screen.blit(BUTTON_FONT.render(short_interval_name, True, WHITE), (coord[0]-9, coord[1]-7))

            else:
                screen.blit(BUTTON_FONT.render(short_interval_name, True, WHITE), (coord[0]-5, coord[1]-7))

        # get start time for duration tracking
        start_time = time.time()

        # choose interval for user to predict
        predict_interval = choose_interval(curr_stats, saved_data)

        # if we get a new prediction item, record it into curr_stats  history
        if len(curr_stats["interval_history"]) == curr_stats["num_correct"] + curr_stats["num_wrong"]:
            curr_stats["interval_history"].append(predict_interval)


        # Get Notes 
        note_a, note_b = predict_interval.note_a, predict_interval.note_b

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
        
            

        note_a_pos = get_note_pos(ALL_NOTES, all_note_pos, note_a)
        note_b_pos = get_note_pos(ALL_NOTES, all_note_pos, note_b)
        

        # draw the Interval connecting the notes
        pygame.draw.line(screen, LIGHT_GREY, note_a_pos, note_b_pos, width=14)

        # draw red box around note_a to tell direction
        x_a, y_a = note_a_pos
        pygame.draw.circle(screen, (235,155,65), (x_a, y_a), NOTE_RADIUS+12)
        pygame.draw.circle(screen, (239,185,95), (x_a, y_a), NOTE_RADIUS+9)

        # draw notes
        pygame.draw.circle(screen, WHITE, note_a_pos, NOTE_RADIUS)
        pygame.draw.circle(screen, WHITE, note_b_pos, NOTE_RADIUS)

        # get user input and do actions

        # stores the (x,y) mouse coordinates in (x, y) tuple
        mouse = pygame.mouse.get_pos()

        # read user inputs
        for ev in pygame.event.get():

            # exit game and cleanup on quit
            if ev.type == pygame.QUIT :
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
                    for saved_interval in saved_data:
                        if intervals_equal(predict_interval, saved_interval):
                            # time to make choice from start
                            guess_time = time.time() - start_time 

                            # add guess to saved note class cached guess storage 
                            guess = Guess(predict_interval.get_full_name(), butt_press_name, guess_time)
                            saved_interval.add_guess(guess)
                   

                    # Generate unique graphics for Incorrect and Correct guesses and record into curr_stats
                    if butt_press_name == predict_interval.get_full_name(): 

                        # record current game stats
                        curr_stats["num_correct"] += 1

                        # create success text
                        success_text = TITLE_FONT.render('CORRECT', True, SUCCESS_GREEN)

                    
                    # record incorrect guess
                    else:
                        curr_stats["num_wrong"] += 1
                        
                        # create failure text
                        success_text = TITLE_FONT.render('WRONG', True, FAILURE_RED)


                    # REVEAL TRUE NOTES
                    
                    note_a_pos = get_note_pos(ALL_NOTES, all_note_pos, note_a)
                    note_b_pos = get_note_pos(ALL_NOTES, all_note_pos, note_b)
                    
                    # draw the Interval connecting the notes
                    pygame.draw.line(screen, combine_colors(note_a.color, note_b.color), note_a_pos, note_b_pos, width=14)

                    # draw red box around note_a to tell direction
                    x_a, y_a = note_a_pos
                    pygame.draw.circle(screen, (235,155,65), (x_a, y_a), NOTE_RADIUS+12)
                    pygame.draw.circle(screen, (239,185,95), (x_a, y_a), NOTE_RADIUS+9)

                    # draw notes
                    pygame.draw.circle(screen, note_a.color, note_a_pos, NOTE_RADIUS)
                    pygame.draw.circle(screen, note_b.color, note_b_pos, NOTE_RADIUS)
                    
                    draw_note_name(note_a)
                    draw_note_name(note_b)

                    # draw the interval name on the midpoint of the line
                    midp_x, midp_y = (note_a_pos[0] + note_b_pos[0])/2, (note_a_pos[1] + note_b_pos[1])/2
                    side_margin = WINDOW_WIDTH / 16
                    vert_margin = side_margin
                    if midp_x > WINDOW_WIDTH / 2:
                        side_margin = -side_margin
                    if midp_y > WINDOW_HEIGHT /2:
                        vert_margin = -vert_margin
                    
                    screen.blit(LABEL_FONT.render(predict_interval.get_full_name(), True, WHITE), (midp_x-50+side_margin, midp_y+vert_margin))

                    # play interval from a to b, then back from b to a
                    min_play, max_play = 300, 1000
                    random_play_len = lambda : random.randint(min_play, max_play)
                    note_a.play_sound(random_play_len())
                    note_b.play_sound(random_play_len())
                    note_a.play_sound(random_play_len())

                    # draw success or wrong text
                    screen.blit(success_text, (WINDOW_WIDTH/2 - 55, WINDOW_HEIGHT - menu_height - (side_padding/2)))
                

                    # update screen
                    pygame.display.update()
                    pygame.time.delay(2000 * DISPLAY_ANSWER_TIME)


                    # save to file
                    save_data(saved_data, SAVED_INTERVALS_FILE)

                    # sort by acc
                    sorted_data = sorted(saved_data, key=lambda x: x.get_accuracy())

                    # every 10x notes print and draw stats
                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    if len(curr_stats["interval_history"]) % 10 == 0:    

                        print("\nHow I'm Doing")
                        for i, interval in enumerate(sorted_data):
                            print(f'{i} {interval.get_short_name()} note a: {interval.note_a.name} note b: {interval.note_b.name} accur: {interval.get_accuracy()} avg time: {interval.get_avg_guess_time()}' )

                        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

                        # I COMMENED (TURNED OFF) THE BELOW DRAW AND PRINT

                        # # PRINTING AND DRAWING STATS TAKES A LONG TIME (~30s)
                        # # SINCE WE HAVE 6083 INTERVALS.

                        # # draw how im doing as bar chart
                        # plt.bar([f'{n.get_short_name()}' for n in saved_data], calc_prob_dist_guessmaker(sorted_data))
                        # plt.title('Weights of Next Interval Pick')
                        # plt.xlabel('Interval')
                        # plt.xticks(fontsize=8, rotation=90)
                        # plt.ylabel('Factor')
                        # plt.savefig('next_interval_prob.png', bbox_inches='tight')

                else:
                    pass


        # updates the frames of the game
        pygame.display.update()
