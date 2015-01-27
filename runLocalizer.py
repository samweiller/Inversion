import os
from expyriment import design, control, stimuli, io, misc
import numpy as np

###### GET SUBJECT PARAMETERS ######
subjectNumber 	= int(raw_input("Please enter the subject number: "))
runNumber 	 	= int(raw_input("Please enter the run number: "))

###### EXPYRIMENT INITIALIZATION ######
exp = design.Experiment("FOSS Localizer")
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
imagePresentationTime = 600 #ms
ISI = 400 #ms
fixationTime = 4000 #ms

# Prep stimuli directories
stimuliPaths = []
subDirectories = ["faces", "objects", "scenes", "scrambled"]
design.randomize.shuffle_list(subDirectories)
subDirectories.extend(subDirectories[::-1])

for directory in subDirectories:
	stimuliPaths.append(os.path.join("/Users/samweiller/Desktop/localizerStimuli", directory))

for condition in stimuliPaths:
	validImages = 0

	conditionName = subDirectories[stimuliPaths.index(condition)]

	b = design.Block(name=conditionName)
	b.set_factor("Condition", conditionName)
	imageNames = [os.path.join(condition, f) for f in os.listdir(condition)]
	imageRandomizer = design.randomize.rand_int_sequence(0, imagesPerBlock)
	for imageNumber in imageRandomizer:
		if validImages < imagesPerBlock:
			if imageNames[imageNumber].endswith('jpg'):
				t = design.Trial()
				soloName = os.path.split(imageNames[imageNumber])[1]
				t.set_factor("Image Name", soloName)

				s = stimuli.Picture(imageNames[imageNumber], (0,0))
				s.scale(scaleFactor)
				t.add_stimulus(s)
				b.add_trial(t, copies=1, random_position=True)

				validImages += 1
			else:
				imageNames.remove(imageNames[imageNumber])
		else:
			break

	#b.shuffle_trials()
	exp.add_block(b)

###### RUN EXPERIMENT ######
# exp.save_design("StatLoc_Subject%02d_design.csv" % subjectNumber)
control.start(subject_id=subjectNumber, skip_ready_screen=True) # Start the experiment

stimuli.TextLine("Experiment is Prepped! Waiting for t to begin...").present()
theKeyboard.wait(keys=misc.constants.K_t)
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

		exp.clock.wait(ISI - fixCross.present())
		# fixCross.present()
		trial.stimuli[0].set_logging(False)
		# exp.clock.wait(ISI/2 -trial.stimuli[0].present())
		# trial.stimuli[0].present()

		exp.clock.wait(imagePresentationTime - trial.stimuli[0].present())
		exp.events.log("Trial End")

	exp.events.log("Block %d Ending :: %d" % (exp.blocks.index(block), exp.clock.time-blockStartTime))

	exp.clock.reset_stopwatch()
	exp.events.log("Post Fixation Start")
	fixCross.present()
	exp.clock.wait(fixationTime)
	exp.events.log("Post Fixation End: %d" % exp.clock.stopwatch_time)

control.end()


