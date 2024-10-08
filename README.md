A massive thank you to Tala Sohrabi (@Talaa202) for teaching me and helping me write this code and to the Balsam-Simpson Lab at the New York State Psychiatric Institute for letting me borrow their Med Associate operant boxes!

# Sustained Attention
## Task Details
In this task the mice are required to press either the right or the left lever in the operant box to retrieve a reward. The "correct" lever the mouse must press in each trial is indicated by light turning on above the lever for a specific time. The mice were trained to reach at least an 80% accuracy rate when the light is on for 10 seconds above a lever. To test their sustained attention the light duration is reduced to 2.5s, then 0.75s, and finally 0.25s. Each cue light duration was presented to the mice for two sessions and the session ended after one hour or 40 rewards.
### Training Overview
After learning how to make a lever press, the mice were trained with force trials. This is when a light is turned on over a lever, but only one lever is presented and when pressed results in a reward. Then choice trials are gradually introduced, this is when both levers are presented but the light is turned on above only one lever so the mice must make a choice to retrive a reward. The code analyzes both choice and force trials so this type of training data can be run. 

## Apparatus Information
The operant boxes were from Med Associates Inc. (Model 1820; Med Associates, St. Albans, VT) and MedScripts were used to run the program (Ward et al., 2015).

## Script Outputs
- Date: date of session 
- Subject: subject number from the Med Associates data file
- Genotype: assigns a value to the subject based on a list defined by the user
- Sex: assigns a value to the subject based on a list defined by the user
- Program: program name from the Med Associates data file
- Session Time: total session time
- Number Of Rewards: number of rewards achieved
- Percent of Choice Trials: percent of trials in the session that were defined as choice trials (the code reads a choice trial as both levers are extended)
- Percent of Correct Choice Trials: the percent of correct (meaning a reward was achieved) choice trials made within all choice trials
- Average Latency: average latency to make a lever press
- Timed Out Trials: times when the lever(s) was presented and no press was made
- Lever Press: number of total lever presses made in the session
- Headpokes Missed: number of times when there was no headpoke during dipper presentation

