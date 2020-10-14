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

sys.path.append("../Utils/")
from Triggers import (setupTriggers, closeTriggers, waitForFMRITrigger, 
                        checkForFMRITrigger, startTriggers, checkForFMRITriggerOrResponse, 
                        MODE_EXP, MODE_DEV, BUTTON_PRESSED, BUTTON_RELEASED)
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
    
    def start(self):
        self.setup()

        run = int(self.expInfo['run'])
        mode = self.expInfo['mode']
        stimList = self.expInfo['list']
        if stimList == 'generate':
            list = ''

        if mode == 'training':
            self.startTraining()
        elif mode == 'experiment':
            self.startExperiment(list, run)
        else:
            print('Unknown mode. Use either "training" or "experiment"')


        
    def startExperiment(self, stimuli_list, run):
        """
        Start the experiment with the specified stimuli list.

        Parameters
        ----------
        stimuli_list : str
            list of stimuli to use. Only specify the name of the list. 
            The respective file should reside in the folder of the python file. Wav-files should be stored in a subfolder "wav" without further subdirectories.
            If stimuli_list is empty, a reandomized list will be generated or used if it is already present. These lists are created for each
            participant and session and are stored in the subfolder 'stim_lists'
        """
        if not stimuli_list:
            filenames, responseTimes = self.generateOrReadStimulusList(run)
        else:
            filenames, responseTimes = self.readStimulusList(stimuli_list)
                
        self.waitForButton(-1, ['space'], 'Press space to start')  
        self.fixation.autoDraw = True
        startTriggers(self)
        self.presentSound('wav' + os.sep + 'Instruktionen.wav')
        self.fixation.autoDraw = False
        waitForFMRITrigger(self, '+')
        logging.log(level = logging.EXP, msg = 'fMRI trigger (first)\t' + str(self.globalClock.getTime()))
        self.fixation.autoDraw = True
        for n in range(0, len(filenames)):
            path = 'wav' + os.sep + filenames[n]
            self.presentSound(path, responseTime=responseTimes[n]/1000)
        self.finish()

    def startTraining(self):
        """
        Start a training run which always uses the standard training stimuli list: stimuli_list_training.csv
        """
        filenames, responseTimes = self.readStimulusList('stimuli_list_training.csv')
        startTriggers(self)
        self.waitForButton(-1, ['space'], 'Press space to start')
        self.presentSound('wav' + os.sep +'Instruktionen.wav')
        self.waitForButton(-1, ['space'], 'Press space to continue')
        self.fixation.autoDraw = False
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
        expInfo = {'mode': 'experiment', 'participant': '', 'session': '001', 'run': '1', 'list': 'generate', 'screen': '0', 'Send triggers': 'yes'}
        dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
        if dlg.OK == False:
            core.quit()  # user pressed cancel
        expInfo['date'] = data.getDateStr()  # add a simple timestamp
        expInfo['expName'] = expName
        expInfo['psychopyVersion'] = self.psychopyVersion
        filename = self._thisDir + os.sep + u'data/%s_%s_%s_%s' % (expInfo['participant'], expName, expInfo['run'], expInfo['date'])
        self.thisExp = data.ExperimentHandler(name=expName, version='',
            extraInfo=expInfo, runtimeInfo=None,
            originPath=self._thisDir + os.sep + 'SemanticIntegration.py',
            savePickle=True, saveWideText=True,
            dataFileName=filename)
        self.logFile = logging.LogFile(filename+'.log', level=logging.EXP)
        logging.console.setLevel(logging.WARNING) 

        #self.serial = serial.Serial(self.serialPort, 19200, timeout=1)

        self.win = visual.Window(
            size=(1024, 768), fullscr=True, screen=int(expInfo['screen']), 
            winType='pyglet', allowGUI=False, allowStencil=False,
            monitor='testMonitor', color='black', colorSpace='rgb',
            blendMode='avg', useFBO=True, 
            units='height')

        # fixation cross
        self.fixation = visual.TextStim(win=self.win, name='fixation',
            text='+',
            font='Arial',
            pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
            color='white', colorSpace='rgb', opacity=1, 
            languageStyle='LTR',
            depth=0.0)
        self.fixation.autoDraw = False

        self.message = visual.TextStim(win=self.win, name='message',
            text='Press key to start',
            font='Arial',
            pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
            color='white', colorSpace='rgb', opacity=1, 
            languageStyle='LTR',
            depth=0.0)
            
        self.expInfo = expInfo
        self.expName = expName
            
        if expInfo['Send triggers'] == "yes":
            setupTriggers(self, MODE_EXP)
        else:
            setupTriggers(self, MODE_DEV)
            
            

    def finish(self):
        """
        Clean up the experiment (close serial port, etc.).
        Output files (data, logs, etc.) are automatically handled by PsychoPy (ExperimentHandler)
        """
        #self.serial.close()
        closeTriggers(self)

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
    
    def getResponseTimeList(self, stimFiles):
        filename = self._thisDir + os.sep + u'responseTimes.csv'
        filenames, responseTimes = self.readStimulusList(filename)

        times = []
        for n in range(0, len(stimFiles)):
            stim = stimFiles[n]
            index = filenames.index(stim)
            times.append(responseTimes[index])

        return times
    
    def writeStimulusList(self, filename, stimuli, responseTimes):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', dialect='excel')
            for i in range(0, len(stimuli)):
                writer.writerow([stimuli[i], responseTimes[i]])

    def generateOrReadStimulusList(self, run):
        stimFile = self._thisDir + os.sep + u'stim_lists\\%s_%s_stim_%s.csv' % (self.expInfo['participant'], self.expInfo['session'], self.expName)

        filenames = []
        responseTimes = []
        if os.path.exists(stimFile):
            print('Using existing stim list')
            filenames, responseTimes = self.readStimulusList(stimFile)
        else:
            print('Generating new stim list')
            filenames, responseTimes = self.generateStimulusList()
            self.writeStimulusList(stimFile, filenames, responseTimes)

        # Select the half corresponding to run 1 or 2
        center = int(len(filenames)/2)
        length = len(filenames)
        if run == 1:
            filenames = filenames[0:center]
            responseTimes = responseTimes[0:center]
        else:
            filenames = filenames[center:length]
            responseTimes = responseTimes[center:length]

        return filenames, responseTimes
    
    def generateStimulusList(self):
        sequenceA = []
        sequenceB = []
        
        expectedA = []
        expectedB = []
        inds = list(range(1, 61))
        np.random.shuffle(inds)
        for i in range(0, 30):
            expectedA.append('expected_' + str(inds[i]) + '.wav')
            sequenceA.append('exp')
        for i in range(30, 60):
            expectedB.append('expected_' + str(inds[i]) + '.wav')
            sequenceB.append('exp')
        
        anomalousA = []
        anomalousB = []
        inds = list(range(1, 61))
        np.random.shuffle(inds)
        for i in range(0, 30):
            anomalousA.append('anomalous_' + str(inds[i]) + '.wav')
            sequenceA.append('an')
        for i in range(30, 60):
            anomalousB.append('anomalous_' + str(inds[i]) + '.wav')
            sequenceB.append('an')
            
        unexpectedA = []
        unexpectedB = []
        inds = list(range(1, 61))
        np.random.shuffle(inds)
        for i in range(0, 30):
            unexpectedA.append('unexpected_' + str(inds[i]) + '.wav')
            sequenceA.append('unexp')
        for i in range(30, 60):
            unexpectedB.append('unexpected_' + str(inds[i]) + '.wav')
            sequenceB.append('unexp')
            
        pseudowordA = []
        pseudowordB = []
        inds = list(range(1, 61))
        np.random.shuffle(inds)
        for i in range(0, 60):
            version = np.random.randint(0, 2)
            if version == 0:
                pseudowordA.append('pseudoword_' + str(inds[i]) + 'a.wav')
                pseudowordB.append('pseudoword_' + str(inds[i]) + 'b.wav')
            else:
                pseudowordA.append('pseudoword_' + str(inds[i]) + 'b.wav')
                pseudowordB.append('pseudoword_' + str(inds[i]) + 'a.wav')
                
            sequenceA.append('pseudo')
            sequenceB.append('pseudo')
            
        
        keepTrying = True
        while(keepTrying):
            # shuffle sequence
            np.random.shuffle(sequenceA)
            
            # test sequence
            ok = self.checkSequence(sequenceA)
            keepTrying = not ok
        
        keepTrying = True
        while(keepTrying):
            # shuffle sequence
            np.random.shuffle(sequenceB)
            
            # test sequence
            ok = self.checkSequence(sequenceB)         
            keepTrying = not ok

        sequence = []
        expectedA = iter(expectedA)
        unexpectedA = iter(unexpectedA)
        anomalousA = iter(anomalousA)
        pseudowordA = iter(pseudowordA)
        for i in range(0, len(sequenceA)):
            if sequenceA[i] == 'exp':
                sequence.append(next(expectedA))
            if sequenceA[i] == 'unexp':
                sequence.append(next(unexpectedA))
            if sequenceA[i] == 'an':
                sequence.append(next(anomalousA))
            if sequenceA[i] == 'pseudo':
                sequence.append(next(pseudowordA))
        
        expectedB = iter(expectedB)
        unexpectedB = iter(unexpectedB)
        anomalousB = iter(anomalousB)
        pseudowordB = iter(pseudowordB)
        for i in range(0, len(sequenceB)):
            if sequenceB[i] == 'exp':
                sequence.append(next(expectedB))
            if sequenceB[i] == 'unexp':
                sequence.append(next(unexpectedB))
            if sequenceB[i] == 'an':
                sequence.append(next(anomalousB))
            if sequenceB[i] == 'pseudo':
                sequence.append(next(pseudowordB))

        responseTimes = self.getResponseTimeList(sequence)
        
        return sequence, responseTimes
        
    def checkSequence(self, sequence):
        ok = True
        for i in range(2, len(sequence)):
            if (sequence[i-2] == sequence[i-1]) and (sequence[i-1] == sequence[i]):
                ok = False
                break
        return ok            

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
        startTimeGlobal = self.globalClock.getTime()
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
                logging.log(level = logging.EXP, msg = 'Playback started\t' + str(self.globalClock.getTime()) + '\t' +wavfile)
            
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
            
            # check for fMRI trigger and responses to log
            trigger, button1, button2 = checkForFMRITriggerOrResponse(self)
            if trigger:
                gt = self.globalClock.getTime()
                logging.log(level = logging.EXP, msg = 'fMRI trigger\t' + str(gt))
            if button1 == BUTTON_PRESSED:
                logging.log(level = logging.EXP, msg = 'Button 1 pressed')
            if button2 == BUTTON_PRESSED:
                logging.log(level = logging.EXP, msg = 'Button 2 pressed')

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
        logging.log(level = logging.EXP, msg = 'Trial ended\t' + str(self.globalClock.getTime()))
        
        self.thisExp.addData('wavfile', wavfile)
        self.thisExp.addData('response', response)
        self.thisExp.addData('rt', rt)
        self.thisExp.addData('wav.started', wav.tStart)
        self.thisExp.addData('startTime', startTime)
        self.thisExp.addData('startTimeGlobal', startTimeGlobal)
        self.thisExp.addData('endTime', endTime)
        self.thisExp.addData('responseTime', responseTime)
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
        
experiment = Experiment()
experiment.start()

