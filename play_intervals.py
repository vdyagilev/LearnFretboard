from play_notes import get_interval_name
import os
from structs import Guess, Interval, Note
from helpers import calc_prob_dist_guessmaker, combine_colors, intervals_equal, load_data, save_data, string_idx_to_letter, zero_one_norm
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


def button_at_pos(coord: tuple) -> str:
    """Return which button is located at (x,y)=coord, or "" if none"""
    for i, interval_name in enumerate(INTERVAL_NAMES):
        # check if y coord within button menu
        dist_between = 118
        width = 40
        height = 40
        horiz_line = 900
        left_padding = 60

        # within vertical zone
        if coord[1] > horiz_line-height and coord[1] < horiz_line+height:
            # within horizontal zone
            if coord[0] > (i*(dist_between)) + left_padding and coord[0] < (i*(dist_between)) + 2*width + left_padding:
                return interval_name

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

    return random.choices(hist_stats, prob_dist, k=1)[0]


        

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
        # iterate thru every pair of notes
        for string_idx_a, notes_lst_a in NOTE_POS.items():
            for string_idx_b, notes_lst_b in NOTE_POS.items():

                for fret_idx_a, note_name_a in enumerate(notes_lst_a):
                    for fret_idx_b, note_name_b in enumerate(notes_lst_b):
                        # init the two Note classes
                        note_a = Note(note_name_a, string_idx_a, fret_idx_a)
                        note_b = Note(note_name_b, string_idx_b, fret_idx_b)

                        # init the Interval class joining them
                        interval = Interval(note_a, note_b)

                        saved_data.append(interval)

        # save initial data list to file
        save_data(saved_data, SAVED_INTERVALS_FILE)

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
    LABEL_FONT = pygame.font.SysFont('Corbel', 32)

    # load fretboard skeleton image
    fretboard_image = pygame.image.load("fretboard-skeleton.png")

    # init screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # rendering a text written in
    # this font
    title = TITLE_FONT.render('Learn Fretboard Intervals', True, VERY_DARK_GREY)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # GAME LOOP
    curr_stats = {"num_correct": 0, "num_wrong": 0, "interval_history": []} # keep track of curr round metrics
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
        for i, interval_name in enumerate(INTERVAL_NAMES):
            # calc location
            left_edge = 300
            right_edge = 1400
            x_step_size = (right_edge - left_edge) / len(INTERVAL_NAMES)

            # draw action button with label
            coord = (100 + i*(x_step_size+1.2*BUTTON_RADIUS), 900)
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

        # draw the Interval connecting the notes
        note_a, note_b = predict_interval.note_a, predict_interval.note_b
        pygame.draw.line(screen, combine_colors(note_a.color, note_b.color), 
            note_a.screen_pos, note_b.screen_pos, width=14)

        # draw red box around note_a to tell direction
        x_a, y_a = note_a.screen_pos
        #x_b, y_b = note_b.screen_pos
        pygame.draw.circle(screen, BEEKEEPER, (x_a, y_a), NOTE_RADIUS+6)
        #pygame.draw.circle(screen, WHITE, (x_b, y_b), NOTE_RADIUS+6)

        # draw notes
        pygame.draw.circle(screen, note_a.color, note_a.screen_pos, NOTE_RADIUS)
        pygame.draw.circle(screen, note_b.color, note_b.screen_pos, NOTE_RADIUS)

        # draw note names
        def draw_note_name(note):
            if "/" in note.name:
                screen.blit(BUTTON_FONT.render(note.name, True, WHITE), (note.screen_pos[0]-18, note.screen_pos[1]-7))
            else:
                screen.blit(BUTTON_FONT.render(note.name, True, WHITE), (note.screen_pos[0]-4, note.screen_pos[1]-7))

        draw_note_name(note_a)
        draw_note_name(note_b)

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

                       
                    # draw the interval name on the midpoint of the line
                    midp_x, midp_y = (note_a.screen_pos[0] + note_b.screen_pos[0])/2, (note_a.screen_pos[1] + note_b.screen_pos[1])/2
                    screen.blit(LABEL_FONT.render(predict_interval.get_full_name(), True, WHITE), (midp_x, midp_y-15))

                    # play tone
                    note_b.play_sound()

                    # draw success or wrong text
                    screen.blit(success_text, (755, 715))
                

                    # update screen
                    pygame.display.update()
                    pygame.time.delay(1000 * DISPLAY_ANSWER_TIME)


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

                        unseen_intervals = list(filter(lambda x: len(x.guesses) == 0, sorted_data))
                        if unseen_intervals:
                            print(f'{len(unseen_intervals)} still unseen.')
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
