### INVERSION
##	Written by Sam Weiller, 2015
##	Contact: sam.weiller@gmail.com

"""
VERSION HISTORY

1.00	2/2/15	Finalized script, ready for deployment pending final test.
	
"""
import os
from expyriment import design, control, stimuli, io, misc
import numpy as np
from csv import reader

###### GET SUBJECT PARAMETERS ######
subjectNumber 	= int(raw_input("Please enter the subject number: "))
runNumber 	 	= int(raw_input("Please enter the run number: "))
threshold 	 	= int(raw_input("Threshold (1), No Thresh (2): "))
CBL 	 	 	= int(raw_input("Please enter the counterbalance number: "))

if threshold == 1:
	isThreshed = "Thresh"
else:
	isThreshed = "NoThresh"

###### EXPYRIMENT INITIALIZATION ######
exp = design.Experiment(name="Inversion", filename_suffix="Run%02d" % runNumber)
control.initialize(exp)
fixCross = stimuli.FixCross()
theKeyboard = exp.keyboard
myKeyboard = io.Keyboard

###### CONTROL PANEL ######
# Define most experimental parameters here.

# Visual Angle
viewingDistance = 1020 #mm
monitorSize = 330 #mm
desiredVA = 6
currentImageSize = 700 #make this dynamic!
newImageSize = np.tan(np.radians(desiredVA/2)) * 2 * viewingDistance * (exp.screen.size[0]*2/monitorSize)
# IMPORTANT: multiply exp.screen.size[0] by 2 if running on a retina display.
scaleFactor = float(newImageSize/currentImageSize)

imagesPerBlock = 20
imagePresentationTime = 250 #ms
firstISI = 500 #ms
secondISI = 1200
fixationTime = 14000 #ms
sameKey = misc.constants.K_f
differentKey = misc.constants.K_j

# Load in stimuli
stimTextFilePath = "/Users/dilkslab/Dropbox/inversion"
stimTextFilename = "%s/stimNames%sCBL%d.csv" % (stimTextFilePath, isThreshed, CBL)
myFilenames = []
csvReader = reader(open(stimTextFilename, 'rb'))
for row in csvReader:
	myFilenames.append(row)

myFilenames = np.swapaxes(myFilenames,0,1)

conditionNames = ["facesUpright", "facesInverted", "scenesUpright", "scenesInverted"]
conditionNames.extend(conditionNames)

imageLocation = "%s/Images" % stimTextFilePath

for blockNumber in range(0,8):
	b = design.Block(name=conditionNames[blockNumber])
	b.set_factor("Condition", conditionNames[blockNumber])
	
	firstImageList = [os.path.join(imageLocation, f) for f in [myFilenames[blockNumber][i] for i in range(len(myFilenames[blockNumber])) if i % 2 == 0]]
	secondImageList = [os.path.join(imageLocation, f) for f in [myFilenames[blockNumber][i] for i in range(len(myFilenames[blockNumber])) if i % 2 == 1]]
	
	for image1 in firstImageList:
		t = design.Trial()

		image2 = secondImageList[firstImageList.index(image1)]

		t.set_factor("Image 1 Name", image1)
		t.set_factor("Image 2 Name", image2)

		s1 = stimuli.Picture(image1, (0,0))
		s1.scale(scaleFactor)
		s2 = stimuli.Picture(image2, (0,0))
		s2.scale(scaleFactor)

		if conditionNames[blockNumber].endswith("Inverted"):
			s1.flip((False,True))
			s2.flip((False,True))

		t.add_stimulus(s1)
		t.add_stimulus(s2)

		b.add_trial(t, copies=1, random_position=True)

	exp.add_block(b)

exp.shuffle_blocks()

###### RUN EXPERIMENT ######
control.start(subject_id=subjectNumber, skip_ready_screen=True) # Start the experiment

stimuli.TextLine("Experiment is Prepped! Waiting for t to begin...").present()
theKeyboard.wait(keys=misc.constants.K_t)
exp.events.log("TRIGGERINIT")
exp.data.add("TRIGGERINIT,%d" % exp.clock.time)

# fixCross.set_logging(False)

for block in exp.blocks:
	exp.events.log("Block %d" % exp.blocks.index(block))
	exp.clock.reset_stopwatch()
	exp.data.add("Fixation Start,0,%d" % exp.clock.time)
	exp.clock.wait(fixationTime-fixCross.present())
	exp.data.add("Fixation End,0,%d,%d" % (exp.clock.time, exp.clock.stopwatch_time))

	exp.events.log(block)
	exp.data.add("Block Start,%d,%d" % (exp.blocks.index(block), exp.clock.time))

	blockStartTime = exp.clock.time

	for trial in block.trials:
		exp.events.log("Trial %d" % block.trials.index(trial))

		exp.clock.wait(imagePresentationTime - trial.stimuli[0].present())
		exp.clock.wait(firstISI - fixCross.present())

		exp.clock.wait(imagePresentationTime - trial.stimuli[1].present())
		fixCross.present()

		(keyPressed, whenPressed) = theKeyboard.wait(duration=secondISI)
		
		if whenPressed != None:
			exp.clock.wait(secondISI-whenPressed)

		if keyPressed == sameKey:
			exp.data.add("%d,%d,same" % (exp.blocks.index(block), block.trials.index(trial)))
		elif keyPressed == differentKey:
			exp.data.add("%d,%d,different" % (exp.blocks.index(block), block.trials.index(trial)))
		elif keyPressed == None:
			exp.data.add("%d,%d,None" % (exp.blocks.index(block), block.trials.index(trial)))
		else:
			exp.data.add("%d,%d,invalid" % (exp.blocks.index(block), block.trials.index(trial)))

	exp.data.add("Block End,%d,%d,%d" % (exp.blocks.index(block), exp.clock.time, exp.clock.time-blockStartTime))
	exp.events.log("Block End,%d,%d,%d" % (exp.blocks.index(block), exp.clock.time, exp.clock.time-blockStartTime))


exp.clock.reset_stopwatch()
exp.data.add("Fixation Start,0,%d" % exp.clock.time)
fixCross.present()
exp.clock.wait(fixationTime)
exp.data.add("Fixation End,0,%d,%d" % (exp.clock.time, exp.clock.stopwatch_time))

control.end()