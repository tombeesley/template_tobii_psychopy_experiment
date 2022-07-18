from psychopy import visual, core, gui, event
import numpy as np
import glob
import csv
import os
import random
import tobii_research as tr
import time
from pathlib import Path

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

f = open('csvfile.csv','w')
f.write('new file\n')
f.close()

runET = 0
writeHeader = True

TS = 0 # variable for PP timestamps 
t_phase = 0 # variable for trial phase information

if runET == 1:
    # connect to eye=tracker
    found_eyetrackers = tr.find_all_eyetrackers()

    my_eyetracker = found_eyetrackers[0]
    print("Address: " + my_eyetracker.address)
    print("Model: " + my_eyetracker.model)
    print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
    print("Serial number: " + my_eyetracker.serial_number)
    print("NEW")  

    def gaze_data_callback(gaze_data):
        # Print gaze points of left and right eye
#        print("Left eye: ({gaze_left_eye}) \t Right eye: ({gaze_right_eye})".format(
#            gaze_left_eye=gaze_data['left_gaze_point_on_display_area'],
#            gaze_right_eye=gaze_data['right_gaze_point_on_display_area']))
        with open('csvfile.csv', 'a', newline = '') as f:  # You will need 'wb' mode in Python 2.x
            
            global writeHeader, trial, t_phase, TS
            
            gaze_data["trial"] = trial
            gaze_data["trial_phase"] = t_phase
            gaze_data["pp_TS"] = TS
            
            w = csv.DictWriter(f, gaze_data.keys())
            if writeHeader == True:
                w.writeheader()
                writeHeader = False
            w.writerow(gaze_data)

winWidth = 1440; winHeight = 810
win = visual.Window(
    size=[winWidth, winHeight],
    units="pix",
    fullscr=False,
    color=[0.5,0.5,0.5])

# read in input files
design_filename = os.path.join(script_dir, "input_files/UNW01_stg1_certain.csv")
my_design = np.genfromtxt(design_filename, delimiter=',', names = True)

#print(my_design)
#print(my_design['cue1'][:])

cue_files_list = glob.glob('img_files\Cue_*.jpg')
imgArray = [visual.ImageStim(win, img, size = 300) for img in cue_files_list] # create array of images

# turn eye-tracker on
if runET == 1: 
    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

for trial in range(1,4):

    cue1 = imgArray[1]
    cue1.pos = [-300,0]
    cue1.draw()
    cue2 = imgArray[2]
    cue2.pos = [300,0]
    cue2.draw()

    # stimulus on
    TS = win.flip()
    t_phase = 1 # start of the "stimulus on" phase
    core.wait(1)

    # stimulus off
    TS = win.flip()
    t_phase = 2 # start of the "stimulus off" phase
    core.wait(.3)

# turn eye-tracker off
if runET == 1: 
    my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)



win.close()