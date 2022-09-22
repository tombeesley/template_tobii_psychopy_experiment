from psychopy import visual, core, event, clock, gui
from psychopy.event import Mouse
import numpy as np
import glob
import csv
import os
import datetime
import random
import tobii_research as tr

random.seed() # use clock for random seed

# Experiment parameters
exp_code = "UNW01" # Unique experiment code
runET = 0
timeout_time = 10

# get current date and time as string
x = datetime.datetime.now()
start_time = x.strftime("%y_%m_%d_%H%M")

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

# GUI for experiment setup and subject details
setupGUI = gui.Dlg(title= exp_code + " Experiment")
setupGUI.addText('Experiment Setup')
setupGUI.addField('Participant Number:', random.randint(1, 999)) # remove random for experiment
setupGUI.addText(' ')  # blank line
setupGUI.addText('Participant details')
setupGUI.addField('Age:')
setupGUI.addField('Gender', choices=["Male", "Female", "Non-binary", "NA", "Other"])
language = setupGUI.addField('English first language?', choices=["Yes", "No"])
setup_data = setupGUI.show()  # show dialog and wait for OK or Cancel
if setupGUI.OK:  # or if ok_data is not None
    subNum = int(setup_data[0])
    print(type(subNum))
    dataFile = "DATA\ " + exp_code + "_" + start_time + "_s" + f"{subNum:03}" + ".csv" # create csv data file
    eye_dataFile = "DATA\ " + exp_code + "_" + start_time + "_s" + f"{subNum:03}" + "_eye.csv"  # create csv data file
else:
    print('Setup cancelled')
    core.quit()

dataHeader = ['exp_code', 'pNum', 'cue1', 'cue2',
              'outcome', 'certainty', 'accuracy', 'RT']
with open(dataFile, 'w', newline='') as f:
    wr = csv.writer(f)
    wr.writerow(dataHeader)

TS = 0 # variable for PP timestamps
t_phase = 0 # variable for trial phase information

#mouse = Mouse(visible=True)

if runET == 1:
    # connect to eye=tracker
    writeHeader = True

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
        with open(eye_dataFile, 'a', newline = '') as f:  # You will need 'wb' mode in Python 2.x

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
    color=[0.5, 0.5, 0.5])

textFeedback = visual.TextStim(win=win, units="pix", pos=[0, -200], color=[-1,-1,-1],
                               font="Arial", height = 20, bold=True)

# read in input files and generate trial sequence

# function for generating trial sequence
def genTrialSeq(design_filename, blocks):
    # read in input files
    stg_design = np.genfromtxt(design_filename, delimiter=',', skip_header = True, dtype = int)
    stg_trials = []

    for b in range(0,blocks):
        newPerm = np.random.permutation(len(stg_design)) # shuffles rows
        stg_trials.append(stg_design[newPerm])

    stg_trials = np.reshape(stg_trials, (-1, 4)) # -1 here signals the missing dimensions, which is auto computed

    return stg_trials

stg1 = genTrialSeq(os.path.join(script_dir, "input_files/UNW01_stg1_certain.csv"), 2)

trialSeq = stg1

# read in image files and create image array for cues
cue_files_list = glob.glob('img_files\Cue_*.jpg')
imgArray = [visual.ImageStim(win, img, size = 300) for img in cue_files_list] # create array of images
imgArray.insert(0, []) # blank element to ensure images start at index 1

# read in instruction slides
instr_files_list = glob.glob('instruction_files\Slide*.PNG')
instrArray = [visual.ImageStim(win, img, size=(winWidth, winHeight)) for img in instr_files_list] # create array of images
timeout_img = instrArray[2] # image for timeout screen
rest_break_img = instrArray[3] # image for rest break screen (not implemented in this task)
debrief_img = instrArray[4] # image for debrief screen

# present the instructions
for instr in range(0, 2):
    instrArray[instr].draw()
    win.flip()
    event.waitKeys(keyList=["space"]) # wait for spacebar response

# turn eye-tracker on
if runET == 1:
    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

for trial in trialSeq[0:4,]:

    # "trial" is the row from trialSeq, containing info on cues/outcomes etc

    cue1 = imgArray[trial[0]]
    cue1.pos = [-300, 0]
    cue1.draw()
    cue2 = imgArray[trial[1]]
    cue2.pos = [300, 0]
    cue2.draw()

    # stimulus on
    TS = win.flip()
    t_phase = 1  # start of the "stimulus on" phase

    keys = event.waitKeys(keyList=["up", "down"], timeStamped=TS, maxWait=timeout_time)  # wait for response
    print(keys)

    acc = 0 # default
    if keys == None:
        timeout_img.draw()
        win.flip()
        core.wait(2)
        acc = -99
        RT = -99  # this signals a timeout
    else:
        if len(keys) == 1:  # check there is only 1 response key pressed
            RT = keys[0][1]
            if keys[0][0] == 'up' and trial[2] == 1:
                feedback = "Correct!"
                acc = 1
            elif keys[0][0] == 'down' and trial[2] == 2:
                feedback = "Correct!"
                acc = 1
            else:
                feedback = "Error!"
        else:  # detected there were multiple keys pressed
            feedback = "Error!"
            RT = -99

        # write feedback text to screen
        textFeedback.text = feedback
        textFeedback.draw()
        TS = win.flip()
        t_phase = 2  # feedback on phase
        core.wait(.5)

    # ITI
    TS = win.flip()
    t_phase = 3  # feedback off, start of ITI phase
    core.wait(1)

    # write details to csv
    trial_data = np.append(trial, [acc, RT])
    trial_data = trial_data.astype(str)
    print(trial_data)
    trial_data = np.insert(trial_data, 0, [exp_code, str(subNum)])

    with open(dataFile, 'a', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(trial_data)

# turn eye-tracker off
if runET == 1:
    my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

debrief_img.draw()
win.flip()
event.waitKeys(keyList=["space"]) # wait for spacebar response

win.close()
