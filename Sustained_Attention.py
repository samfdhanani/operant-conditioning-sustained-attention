import os
import pandas as pd
import numpy as np
from statistics import mean
import matplotlib.pyplot as plt

# declaring empty list
filelist = []
pathslist = []

datapath = os.path.normpath("filepath") #add filepath here
IDList = [1, 2, 3, 4] 
# list of subject IDs as labelled in MED-PC

# walks through the filepath, filelist contains a list of all files and pathslist contains datapaths for subfolders
for subdir, dirs, files in sorted(os.walk(datapath)):
    filelist.append(files)
    pathslist.append(subdir)

filelist.pop(0) # get rid of elements in index zero
pathslist.pop(0) # get rid of elements in index zero

# this function is used to isolate and analyze a specific folder/date from the data; run at the botton of this script
def query(pathslist, querydate): 
    folderdates = []
    for x in pathslist:
        folderdates.append(os.path.basename(os.path.normpath(x))) # extracts the date from the filepath

    querypaths = []

    for i in range(0, len(folderdates)):
        if folderdates[i] == querydate: # 
            querypaths.append(pathslist[i]) # pull specific date

    return(querypaths)

# this function extracts data from each specific data file by ID 
def data_pull(datapath, ID):
    df = []
    progline = None
    
    for subdir, dirs, files in sorted(os.walk(datapath)): # 
        for file in files:
            temp = file.split('.') # split string by '.', in this case the string is split into the sesion date (0) and Subject ID (1)
            sub = temp[1] # Subject ID
            if ID == sub:
                x = os.path.join(subdir, file) # specific file
                df = pd.read_csv(x, sep="[:\s]{1,}", skiprows=15, header=None, engine="python") # skips 15 rows to where the data actually starts
                progline = pd.read_csv(x, skiprows=12, nrows = 1, header = None, engine="python") # reads only 1 row, the program line in the 12th row
                progline = progline.values.tolist()
                progline = progline[0][0].split(" ") 
                if "_" in progline[1]:
                    progline = progline[1].split("_", 1) # splits up program name if an underscore is present
                progline = progline[1]
                df = df.drop(0,axis=1) # cleaning up the data
                df = df.stack() 
                df = df.to_frame() 
                df = df.to_numpy() # dataframe should be an array of each line containing the data, removed the row labels from the data file 
    return(df, progline)   

# this function uses event and timestamp data to output various metrics describing behavior
def data_construct(data): 

    events = np.remainder(data,10000) # use division to isolate event code
    times = data - events # subtract event code from full code

    StartTrial = times[np.where(events == 111)] # all event codes come from the MED-PC Medscript
    StartSess = times[np.where(events == 113)]
    EndSess = times[np.where(events == 114)]

    Sess_time = np.divide(np.subtract(EndSess, StartSess), 10000000)
    Sess_time = Sess_time.tolist() # turn into list
    Sess_time = Sess_time[0] # points to specific info we need

    LLever = times[np.where(events == 27)] # command for when the lever is on
    RLever = times[np.where(events == 28)]

    Lever_extensions = np.concatenate((LLever, RLever), axis = 0) # total time a lever was extended
    Lever_extensions = np.unique(Lever_extensions) # makes sure each time is only recorded once

    LLever_off = times[np.where(events == 29)] # command for when the lever is off
    RLever_off = times[np.where(events == 30)]

    Levers_off = np.concatenate((LLever_off, RLever_off), axis = 0)
    Levers_off = np.unique(Levers_off) 

    DipOn = times[np.where(events == 25)]
    DipOff = times[np.where(events == 26)]
    DipOff = DipOff.tolist()
    if DipOff: # sets DipOff to zero when the list is empty
        DipOff = DipOff[0]
    else:
        DipOff = 0   

    HeadPoke = times[np.where(events == 1011)] 

    if len(Lever_extensions) != len(Levers_off): # remove last lever extension if the lever was not retracted before the program ended
        Lever_extensions = Lever_extensions[:-1] 

    Lever_out_dur = np.divide(np.subtract(Levers_off, Lever_extensions), 10000000) # duration the levers were out

    Reward = times[np.where(events == 25)]

    LeftTrials = times[np.where(events == 31)] # event code is when light turns on to indicate correct lever
    RightTrials = times[np.where(events == 41)] 

    Trial_side = np.concatenate((LeftTrials, RightTrials), axis = 0)
    Trial_side = sorted(Trial_side) # combine left and right trials into a sorted list

    NoInitTrials = [] # list of trials without a response

    for i in range(0,len(Lever_out_dur)):
        if Lever_out_dur[i] == 10.01:
            NoInitTrials.append(i) # instances when the animal does not make a choice, 

    if len(NoInitTrials) != 0: # if there are trials, delete these indexes, don't count to final data
        Lever_extensions = np.delete(Lever_extensions, NoInitTrials)
        Levers_off = np.delete(Levers_off, NoInitTrials)
        Trial_side = np.delete(Trial_side, NoInitTrials)

    trialtype = [] # 0 for forced, 1 for choice, 

    for LeverOut in Lever_extensions:
        L = LLever.tolist() # numpy arrays, if both in the list then define as 1
        R = RLever.tolist()

        if LeverOut in L and LeverOut in R: # defines a choice trial as when both levers are out
            trialtype.append(1)
        else:
            trialtype.append(0) # a force trial is when only one lever is out

    trialside = [] # stores the side each lever press is supposed to be made by the mouse, 

    for t in Trial_side:
        L = LeftTrials.tolist()
        R = RightTrials.tolist()

        if t in L:
            trialside.append('l')
        elif t in R:
            trialside.append('r')


    LPress = times[np.where(events == 1015)]
    RPress = times[np.where(events == 1016)]

    LeverPress = np.concatenate((LPress, RPress),axis=0)
    LeverPress = sorted(LeverPress) # combine lever presses into one list and keep them sorted

    LeverPressList = [] # new array with the side of a lever press sorted
    for p in LeverPress:
        if p in LPress:
            LeverPressList.append('l') 
        elif p in RPress:
            LeverPressList.append('r')
    
    ChoiceTrials = 0 # number of choice trials
    CorrectTrials = 0 # number of correct trials

    for Ttype, side, Lp in zip(trialtype, trialside, LeverPressList): 
        if Ttype == 1: # if the trial is a choice trial
            ChoiceTrials += 1 # add one
            if side == Lp: # if side (correct choice) = lever press (choice made)
                CorrectTrials += 1

# calculate percent of correct choice trials
    if ChoiceTrials != 0: # if choice trials are present (accounts for training programs with only force trials)
        PercCorrect = (CorrectTrials/ChoiceTrials) * 100
    else:
        PercCorrect = None
# calculate percent of choice trials in the session
    PercChoice = ChoiceTrials/len(Trial_side)*100

# number of missed headpoke code
    headpoke_count = 0 # counts the number of headpokes
    within_dipper = False # tracks if dipper is active
    headpoke_occurred = False # tracks if headpoke happens

    for event in events:
        if event == 25:  # DipOn
            within_dipper = True 
        elif event == 26:  # DipOff
            within_dipper = False
            headpoke_occurred = False

        if within_dipper and event == 1011 and not headpoke_occurred:
            headpoke_count += 1
            headpoke_occurred = True

    no_headpoke_count = len(DipOn) - headpoke_count  

# print statements for troubleshooting

    print('Mouse - ', Full_ID)
    print('Total Trials:', len(Trial_side))
    print('Choice Trial Performance:', CorrectTrials, '/', ChoiceTrials)
    print('Percentage Choice Trials Correct:', PercCorrect)   
    print('Timed Out Trials:', len(NoInitTrials))
    
# mean latency calculation

    latencies = np.divide(np.subtract(LeverPress, Lever_extensions), 10000000)
    mean_latency = mean(latencies.tolist())
    x = 0      

    return(Sess_time, len(Reward), PercChoice, PercCorrect, mean_latency, len(NoInitTrials), len(LeverPress), no_headpoke_count)

# assigns a label for genotype to the subject
def genotype(sub):
    g_type = None
    if sub == 1 or sub == 2:
        g_type = 'WT'
    elif sub == 3 or sub == 4:
        g_type = 'Het'

    return g_type

# assigns a label for sex to the subject
def sex(sub):
    s_type = None
    if sub == 1 or sub == 3:
        s_type = 'M'
    elif sub == 2 or sub == 4:
        s_type = 'F'

    return s_type


# uncomment the line below to analyze one specific day in the data, date must match folder name
# pathslist = query(pathslist, '6-14-22')

df_ind = 0 # index variable, add one everytime we run through a subject

# comment the line below when running the script for one day only 
sus_attn_df = pd.DataFrame(columns = ['Date', 'Subject', 'Genotype', 'Sex','Program', 'Session Time', 'Number Of Rewards', 'Percent of Choice Trials', 'Percent of Correct Choice Trials', 'Average Latency', 'Timed Out Trials', 'Lever Press', 'Headpokes Missed'])

def new_func(session_type, ID, progline):
    sess_type = session_type(progline, ID)
    return sess_type
def get_genotype(ID): # defines a function using ID and stores the genotype labels in g_type 
    g_type = genotype(ID)
    return g_type
def get_sex(ID): # defines a function using ID and stores the sex labels in s_type
    s_type = sex(ID)
    return s_type

for dirs in pathslist:

    date = os.path.basename(os.path.normpath(dirs))
    # uncomment the line below to analyze one specific day in the data
    # sus_attn_df = pd.DataFrame(columns = ['Date', 'Subject', 'Genotype', 'Sex','Program', 'Session Time', 'Number Of Rewards', 'Percent of Choice Trials', 'Percent of Correct Choice Trials', 'Average Latency', 'Timed Out Trials', 'Lever Press', 'Headpokes Missed'])
    csv_name = ".csv"
    
    for ID in IDList: # run through ID list one by one, add 'Subject' to this to prevent confusion
        Full_ID = "Subject " + str(ID)
        data, progline = data_pull(dirs, Full_ID) # calling datapull and putting it through dirs
        if len(data) == 0:
            continue
        Sess_time, num_Rewards, PercChoice, PercCorrect, mean_latency, TO_trials, num_LeverPress, no_headpoke_count = data_construct(data) #data construct, putting that all here
        g_type = get_genotype(ID)
        s_type = get_sex(ID)
        # comment the line below to analyze one specific day in the data
        sus_attn_df.loc[df_ind] = [date, Full_ID, g_type, s_type, progline, Sess_time, num_Rewards, PercChoice, PercCorrect, mean_latency, TO_trials, num_LeverPress, no_headpoke_count] #assigning variables one by one
        df_ind += 1 # location zero is populated with variables above, add one each time for it to be sequential

    # uncomment the line below to analyze one specific day in the data
    # sus_attn_df.to_csv(dirs + csv_name)

# comment the line below to analyze one specific day in the data
sus_attn_df.to_csv(datapath + "_DATE.csv")