from __future__ import absolute_import, division

from psychopy import locale_setup
from psychopy import prefs
from psychopy import gui, visual, core, data, event, logging, clock
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import sys  # to get file system encoding

from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB']
from psychopy import sound

from psychopy.hardware import keyboard
import serial

import csv

# specify mode here: training or experiment
mode = 'training'

# specify stimuli list to use (not necessary for training which always uses stimuli_list_training.csv)
stimuliList = 'stimuli_list1_session1.csv'

class Experiment:
    
    def __init__(self):
        """
        Constructor which sets up a number of general attributes and defaults.
        """
        self.pauseClock = core.Clock()        
        self.psychopyVersion = '3.2.4'
        self.globalClock = core.Clock()  # to track the time since experiment started
        self.routineTimer = core.CountdownTimer()
        self.defaultKeyboard = keyboard.Keyboard()
        self.frameTolerance = 0.001 
        self.endExpNow = False
        #self.serialPort = 'COM1'
        
    def startExperiment(self, stimuli_list):
        """
        Start the experiment with the specified stimuli list.

        Parameters
        ----------
        stimuli_list : str
            list of stimuli to use. Only specify the name of the list. 
            The respective file should reside in the folder of the python file. Wav-files should be stored in a subfolder "wav" without further subdirectories.
        """
        filenames, responseTimes = self.readStimulusList(stimuli_list)
        self.setup()
        self.waitForButton(-1, ['space'], 'Press space to start')  
        self.presentSound('wav' + os.sep + 'Instruktionen.wav')
        self.waitForButton(-1, ['space'], 'Press space to continue')
        for n in range(0, len(filenames)):
            path = 'wav' + os.sep + filenames[n]
            self.presentSound(path, responseTime=responseTimes[n]/1000)
        self.finish()

    def startTraining(self):
        """
        Start a training run which always uses the standard training stimuli list: stimuli_list_training.csv
        """
        filenames, responseTimes = self.readStimulusList('stimuli_list_training.csv')
        self.setup()
        self.waitForButton(-1, ['space'], 'Press space to start')
        self.presentSound('wav' + os.sep +'Instruktionen.wav')
        self.waitForButton(-1, ['space'], 'Press space to continue')
        for n in range(0, len(filenames)):
            path = 'wav' + os.sep + filenames[n]
            self.presentSound(path, responseTime=responseTimes[n]/1000)
        self.finish()

    def setup(self):
        """
        Setup experiment info, log file and window
        """
        self._thisDir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self._thisDir)
        expName = 'SemanticIntegration'  # from the Builder filename that created this script
        expInfo = {'participant': '', 'session': '001'}
        dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
        if dlg.OK == False:
            core.quit()  # user pressed cancel
        expInfo['date'] = data.getDateStr()  # add a simple timestamp
        expInfo['expName'] = expName
        expInfo['psychopyVersion'] = self.psychopyVersion
        filename = self._thisDir + os.sep + u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])
        self.thisExp = data.ExperimentHandler(name=expName, version='',
            extraInfo=expInfo, runtimeInfo=None,
            originPath=self._thisDir + os.sep + 'SemanticIntegration.py',
            savePickle=True, saveWideText=True,
            dataFileName=filename)
        self.logFile = logging.LogFile(filename+'.log', level=logging.EXP)
        logging.console.setLevel(logging.WARNING) 

        #self.serial = serial.Serial(self.serialPort, 19200, timeout=1)

        # windowed mode for now for easier debugging
        self.win = visual.Window(
            size=(1024, 768), fullscr=True, screen=0, 
            winType='pyglet', allowGUI=False, allowStencil=False,
            monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
            blendMode='avg', useFBO=True, 
            units='height')
        
        self.message = visual.TextStim(win=self.win, name='message',
            text='Press key to start',
            font='Arial',
            pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
            color='black', colorSpace='rgb', opacity=1, 
            languageStyle='LTR',
            depth=0.0)

    def finish(self):
        """
        Clean up the experiment (close serial port, etc.).
        Output files (data, logs, etc.) are automatically handled by PsychoPy (ExperimentHandler)
        """
        #self.serial.close()

    def readStimulusList(self, filename):
        """
        Read the specified stimuli list (csv-file with wavefile in the first and response time (in ms) in the second column) 
        
        Parameters
        ----------
        filename : str
            file to read (either absolute path or relative to the folder of the python file)
        """
        filenames = []
        responseTimes = []
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile, dialect='excel')
            for row in reader:
                tokens = row[0].split(';')
                filenames.append(tokens[0])
                responseTimes.append(int(tokens[1]))

        return filenames, responseTimes

    def presentSound(self, wavfile, responseTime=0, keyList=['1', '2']):
        """
        Play a sound with additional time to wait for a key response. 
        Response and reaction time relative to the end of the wave file are recorded.
        
        Parameters
        ----------
        wavfile : str 
            wave file to play (either absolute path or relative to the folder of the python file)
        responseTime: double
            time in seconds to wait for a response after the end of the wave file (default: 0s)
        keyList : list of str
            list of keys to record as response. Only the first key is recorded and the response does not end the trial (default: 1 and 2)
        """
        trialClock = core.Clock()
        wav = sound.Sound(wavfile, secs=-1, stereo=True, hamming=True, name="sound stimulus")
        wav.setVolume(1)
        trialDuration = wav.getDuration() + responseTime
        keyb = keyboard.Keyboard()

        trialComponents = [wav]    
        self.resetTrialComponents(trialComponents)

        response = ''
        rt = -1
        resetDone = False

        # reset timers
        t = 0
        startTime = trialClock.getTime()
        _timeToFirstFrame = self.win.getFutureFlipTime(clock="now")
        trialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        continueRoutine = True

        while continueRoutine:
            # get current time
            t = trialClock.getTime()
            tThisFlip = self.win.getFutureFlipTime(clock=trialClock)
            tThisFlipGlobal = self.win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            if wav.status == NOT_STARTED and t >= 0.0-self.frameTolerance:
                # keep track of start time/frame for later
                wav.frameNStart = frameN  # exact frame index
                wav.tStart = t  # local t and not account for scr refresh
                wav.tStartRefresh = tThisFlipGlobal  # on global time
                wav.play()  # start the sound (it finishes automatically)
            
            # Check for a response. This doesn't need to be sychronized with the next 
            # frame flip
            if wav.status == FINISHED and rt == -1:
                if resetDone:
                    theseKeys = keyb.getKeys(keyList=keyList, waitRelease=False)
                    if len(theseKeys):
                        response = theseKeys[0].name
                        rt = theseKeys[0].rt 
                else:
                    keyb.clock.reset()
                    resetDone = True

            # check for quit (typically the Esc key)
            if self.endExpNow or self.defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()
            
            if wav.status == FINISHED and tThisFlipGlobal > wav.tStartRefresh + trialDuration-self.frameTolerance:
                continueRoutine = False     
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                self.win.flip()

        # -------Ending Routine -------
        wav.stop()  # ensure sound has stopped at end of routine
        endTime = trialClock.getTime()
        
        self.thisExp.addData('wavfile', wavfile)
        self.thisExp.addData('response', response)
        self.thisExp.addData('rt', rt)
        self.thisExp.addData('wav.started', wav.tStart)
        self.thisExp.addData('startTime', startTime)
        self.thisExp.addData('endTime', endTime)
        self.thisExp.nextEntry()
        
        self.routineTimer.reset()

    def resetTrialComponents(self, components):
        """
        Reset the specified list of PsychoPy-components.
        
        Parameters
        ----------
        components : list of PsychoPy components
            list of PsychoPy components to reset
        """
        for thisComponent in components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            #if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED


    def waitForButton(self, maxTime, keyList, text):
        """
        Wait for a button press.
        
        Parameters
        ----------
        maxTime : double
            maximum time in seconds to wait for a button press.
            If -1 is specified, the function waits until a button press with no limit
        keyList : list of str
            keys to wait for
        """
        t = 0
        _timeToFirstFrame = self.win.getFutureFlipTime(clock="now")
        self.pauseClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        continueRoutine = True
        key_resp = keyboard.Keyboard()
        self.resetTrialComponents([key_resp])
        self.message.text = text
        
        while continueRoutine:
            # get current time
            t = self.pauseClock.getTime()
            tThisFlip = self.win.getFutureFlipTime(clock=self.pauseClock)
            tThisFlipGlobal = self.win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *key_resp* updates
            waitOnFlip = False
            if key_resp.status == NOT_STARTED and tThisFlip >= 0.0-self.frameTolerance:
                # keep track of start time/frame for later
                key_resp.frameNStart = frameN  # exact frame index
                key_resp.tStart = t  # local t and not account for scr refresh
                key_resp.tStartRefresh = tThisFlipGlobal  # on global time
                self.win.timeOnFlip(key_resp, 'tStartRefresh')  # time at next scr refresh
                key_resp.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                self.win.callOnFlip(key_resp.clock.reset)  # t=0 on next screen flip
                self.win.callOnFlip(key_resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
                self.message.setAutoDraw(True)
            if key_resp.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if maxTime >= 0 and tThisFlipGlobal >  key_resp.tStartRefresh + maxTime-self.frameTolerance:
                    # keep track of stop time/frame for later
                    key_resp.tStop = t  # not accounting for scr refresh
                    key_resp.frameNStop = frameN  # exact frame index
                    self.win.timeOnFlip(key_resp, 'tStopRefresh')  # time at next scr refresh
                    key_resp.status = FINISHED
            if key_resp.status == STARTED and not waitOnFlip:
                theseKeys = key_resp.getKeys(keyList=keyList, waitRelease=False)
                if len(theseKeys):
                    theseKeys = theseKeys[0]  # at least one key was pressed
                    
                    # check for quit:
                    if "escape" == theseKeys:
                        self.endExpNow = True
                    key_resp.keys = theseKeys.name  # just the last key pressed
                    key_resp.rt = theseKeys.rt
                    # a response ends the routine
                    continueRoutine = False
                    key_resp.status = FINISHED
            
            # check for quit (typically the Esc key)
            if self.endExpNow or self.defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()
            
            continueRoutine = False  # will revert to True if at least one component still running
            
            if key_resp.status != FINISHED:
                continueRoutine = True
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                self.win.flip()

        # -------Ending Routine "pause"-------
        
        self.message.setAutoDraw(False)
        
        # check responses
        if key_resp.keys in ['', [], None]:  # No response was made
            key_resp.keys = None
        self.thisExp.addData('key_resp.keys',key_resp.keys)
        if key_resp.keys != None:  # we had a response
            self.thisExp.addData('key_resp.rt', key_resp.rt)
        self.thisExp.addData('key_resp.started', key_resp.tStartRefresh)
        self.thisExp.addData('key_resp.stopped', key_resp.tStopRefresh)
        self.thisExp.nextEntry()

    def waitForSerial(self, numberOfSignals):
        """
        Wait for a number of serial port signals (e.g. MRI scanner pulses)

        Parameters
        ----------
        numberOfSignals : int
            number of signals to wait for
        """
        continueRoutine = True
        detected = 0
        while continueRoutine:
            value = self.serial.read()

            # Determine here if the values constitue a signal (TODO)
            if value > 0:
                detected = detected + 1

            if detected >= numberOfSignals:
                continueRoutine = False
        

# Use this for command line usage
# if len(sys.argv) == 1:
#     print('Format: python.exe SemanticIntegration.py <mode> <stimuli list>')
#     print('mode: Either "training" or "experiment".')
#     print('training: use the standard training list (stimuli_list_training.csv) to practice before the actual experiment. If a stimuli list is specified, it will be ignored.')
#     print('experiment: perform the actual experiment. In this case, the stimuli list needs to be specified.')
# else:
#     mode = sys.argv[1]
#     if mode == "training":
#         print('Training mode')
#         experiment = Experiment()
#         experiment.startTraining()
#     elif mode == "experiment":
#         print('Experiment mode using ' + sys.argv[2])
#         experiment = Experiment()
#         experiment.startExperiment(sys.argv[2])
#     else:
#         print('Unknown mode: ' + mode + '. Only "training" or "experiment" are allowed.')

# Comment out this for use from PsychoPy Coder
# Options are listed at the very top of this file for easier access
if mode == "training":
    print('Training mode')
    experiment = Experiment()
    experiment.startTraining()
elif mode == "experiment":
    print('Experiment mode using ' + stimuliList)
    experiment = Experiment()
    experiment.startExperiment(stimuliList)
else:
    print('Unknown mode: ' + mode + '. Only "training" or "experiment" are allowed.')

