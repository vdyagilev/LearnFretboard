from structs import Guess, Note
from helpers import calc_prob_dist_guessmaker, get_interval_name, load_data, notes_equal, save_data, string_idx_to_letter, zero_one_norm
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
    """Returns a note for user to predict. Returns with probability based on past success"""
    total_pred = curr_stats["num_correct"] + curr_stats["num_wrong"]

    # user has yet to predict last given note
    if len(curr_stats["note_history"]) > total_pred:
        return curr_stats["note_history"][-1]
    
    # get zero-one normalized prob dist based on time and accuracy
    prob_dist = calc_prob_dist_guessmaker(hist_stats)

    # add small number to ensure zero one is not zero anymore
    SMALL_NUM = (1/78)
    prob_dist = [x + SMALL_NUM for x in prob_dist]


    return random.choices(hist_stats, prob_dist, k=1)[0]
        

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

    # init pygame
    pygame.init()

    # init sound library
    pygame.mixer.init(SAMPLE_RATE,-16,2,512)

    # change window title
    pygame.display.set_caption('LearnFretboard')

    # init pygame related constants

    # default font
    TITLE_FONT = pygame.font.SysFont('Corbel', 51)
    BUTTON_FONT = pygame.font.SysFont('Corbel', 21)
    LABEL_FONT = pygame.font.SysFont('Corbel', 42)

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
        screen.fill((223, 230, 233))
        pygame.draw.rect(screen, (99, 110, 114), (0, WINDOW_HEIGHT-220, WINDOW_WIDTH, 20))
        pygame.draw.rect(screen, (45, 52, 54), (0, WINDOW_HEIGHT-200, WINDOW_WIDTH, 200))


        # draw freboard skeleton image
        screen.blit(fretboard_image, (0, 0))

        # draw title
        screen.blit(title, (630, 40))

        # draw num_correct and num_wrong this round
        num_correct_title = LABEL_FONT.render(f'Correct: {curr_stats["num_correct"]}', True, DARK_GREY)
        num_wrong_title = LABEL_FONT.render(f'Wrong: {curr_stats["num_wrong"]}', True, DARK_GREY)
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
            pygame.draw.line(screen, BEEKEEPER, last_note.get_screen_pos(), predict_note.get_screen_pos(), width=8)
            # draw name of interval
            midp_x, midp_y = (last_note.get_screen_pos()[0] + predict_note.get_screen_pos()[0])/2, (last_note.get_screen_pos()[1] + predict_note.get_screen_pos()[1])/2
            
            # draw circle, and interval name on top

            # draw a grey note for user to predict
            pygame.draw.circle(screen, LIGHT_GREY, predict_note.get_screen_pos(), NOTE_RADIUS)

            interval_name = get_interval_name(last_note, predict_note)
        
            screen.blit(BUTTON_FONT.render(interval_name, True, WHITE), (midp_x, midp_y-15))
        
        else:
            # draw a grey note for user to predict
            pygame.draw.circle(screen, LIGHT_GREY, predict_note.get_screen_pos(), NOTE_RADIUS)
        


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
                    pygame.draw.circle(screen, predict_note.color, predict_note.get_screen_pos(), NOTE_RADIUS)
                    if "/" in predict_note.name:
                        screen.blit(BUTTON_FONT.render(predict_note.name, True, WHITE), (predict_note.get_screen_pos()[0]-18, predict_note.get_screen_pos()[1]-7))
                    else:
                        screen.blit(BUTTON_FONT.render(predict_note.name, True, WHITE), (predict_note.get_screen_pos()[0]-4, predict_note.get_screen_pos()[1]-7))

                    # play tone
                    predict_note.play_sound(1000)

                    # draw success or wrong text
                    screen.blit(success_text, (755, 715))
                    
                    # draw fret and string 
                    screen.blit(loc_text, (760, 750))

                    # update screen
                    pygame.display.update()
                    pygame.time.delay(1000 * DISPLAY_ANSWER_TIME)


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
