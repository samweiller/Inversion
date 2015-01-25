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
exp = design.Experiment("Static Dog Localizer")
exp.data.__init__("Run%02d" % runNumber, time_stamp=False)
control.initialize(exp)
fixCross = stimuli.FixCross()
theKeyboard = exp.keyboard
myKeyboard = io.Keyboard
exp.events.__init__("Run%02d" % runNumber, time_stamp=False)

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
fixationTime = 1000 #ms

# Load in stimuli
stimTextFilePath = "/Users/samweiller/Dropbox-Dilks/Dropbox/inversion"
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
exp.save_design("StatLoc_Subject%02d_design.csv" % subjectNumber)
control.start(subject_id=subjectNumber, skip_ready_screen=True) # Start the experiment

stimuli.TextLine("Experiment is Prepped! Waiting for R...").present()
theKeyboard.wait(keys=misc.constants.K_r)
exp.events.log("INITIAL TRIGGER")

fixCross.set_logging(False)

for block in exp.blocks:
	exp.clock.reset_stopwatch()
	exp.events.log("Pre Fixation Start")
	fixCross.present()
	exp.clock.wait(fixationTime)
	exp.events.log("Pre Fixation End: %d" % exp.clock.stopwatch_time)

	exp.events.log(block)
	exp.events.log("Starting Block %d" % exp.blocks.index(block))

	blockStartTime = exp.clock.time

	for trial in block.trials:
		exp.clock.reset_stopwatch()
		exp.events.log("Trial %02d Start" % block.trials.index(trial))
		exp.events.log(trial.get_factor("Image Name"))

		exp.clock.wait(imagePresentationTime - trial.stimuli[0].present())
		exp.clock.wait(firstISI - fixCross.present())

		exp.clock.wait(imagePresentationTime - trial.stimuli[1].present())
		fixCross.present()

		# keyPressed = exp.clock.wait(secondISI, function = keyPressed = theKeyboard.check())

		(keyPressed, whenPressed) = theKeyboard.wait(duration=secondISI-3)
		
		if whenPressed == None:
			whenPressed = secondISI

		exp.clock.wait(secondISI-whenPressed)


		# print keyPressed

		# fixCross.present()
		# trial.stimuli[0].set_logging(False)
		# exp.clock.wait(ISI/2 -trial.stimuli[0].present())
		# trial.stimuli[0].present()

		# exp.clock.wait(imagePresentationTime - trial.stimuli[0].present())
		exp.events.log("Trial End")



	exp.events.log("Block %d Ending :: %d" % (exp.blocks.index(block), exp.clock.time-blockStartTime))

exp.clock.reset_stopwatch()
exp.events.log("Post Fixation Start")
fixCross.present()
exp.clock.wait(fixationTime)
exp.events.log("Post Fixation End: %d" % exp.clock.stopwatch_time)


#print imageNames
control.end()


