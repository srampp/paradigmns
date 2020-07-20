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

# Alice in Wonderland localizer according to Fedorenko et al.
# Issues to add/decide:
# - PsychoPy ties its timing to the framerate of the presenting monitor/projector. Since this paradigm is 
#   auditory only (except for the constantly shown fixation cross), we may want to drop this. Then again,
#   it probably doesn't cause any issues, as this might induce only a slight variation of a few milliseconds.
# - Waiting for scanner triggers to synchronize the presentation of blocks is not implemented yet
# - Buffering: The wav-files are loaded into memory at the start of the respective block. This should be rather quick,
#   however, Fedorenko et al. do this at the end of the previous block. We may to adjust this or take yet
#   another approach and load all required wav-files into memory during setup. The total amount of required 
#   memory should not be too bad, as we're looking at ~4.5Mb per intact/degraded pair, so 12*4.5Mb = 540Mb.

# Set of audio files to use: 1 - files 1-12, 2 - files 13-24
set = 1

# Language of the stimuli
language = 'German'



class AliceLocalizer:

    def __init__(self):
        """
        Constructor which sets up a number of general attributes and defaults.

        Parameters
        ----------
        stimuliDir : string
            path to the directory containing the stimulus files/subdirecories
        """
        self.pauseClock = core.Clock()        
        self.psychopyVersion = '3.2.4'
        self.globalClock = core.Clock()  # to track the time since experiment started
        self.routineTimer = core.CountdownTimer()
        self.defaultKeyboard = keyboard.Keyboard()
        self.frameTolerance = 0.001 
        self.endExpNow = False
        #self.serialPort = 'COM1'
        
    def setup(self):
        """
        Setup experiment info, log file and window
        """
        self._thisDir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self._thisDir)
        self.stimuliDir = os.path.join(self._thisDir, 'stimuli')
        expName = 'AliceLocalizer'
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

        self.win = visual.Window(
            size=(1024, 768), fullscr=True, screen=0, 
            winType='pyglet', allowGUI=False, allowStencil=False,
            monitor='testMonitor', color='white', colorSpace='rgb',
            blendMode='avg', useFBO=True, 
            units='height')

        # fixation cross
        self.fixation = visual.TextStim(win=self.win, name='fixation',
            text='+',
            font='Arial',
            pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
            color='black', colorSpace='rgb', opacity=1, 
            languageStyle='LTR',
            depth=0.0)
        self.fixation.autoDraw = True

        self.message = visual.TextStim(win=self.win, name='message',
            text='Press key to start',
            font='Arial',
            pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
            color='black', colorSpace='rgb', opacity=1, 
            languageStyle='LTR',
            depth=0.0)
        self.fixation.autoDraw = False

        # block sequence
        # X = fixate
        # I = intact
        # D = degraded
    
        self.blocks = ['X', 'I', 'D', 'I', 'D', 'X', 'I', 'D', 'D', 'I', 'X', 'D', 'I', 'D', 'I', 'X',
            'X', 'D', 'I', 'D', 'I', 'X', 'D', 'I', 'I', 'D', 'X', 'I', 'D', 'I', 'D', 'X']

    def finish(self):
        """
        Clean up the experiment (close serial port, etc.).
        Output files (data, logs, etc.) are automatically handled by PsychoPy (ExperimentHandler)
        """
        self.serial.close()
            
    def startExperiment(self, set = 1, language = 'German'):
        """
        Start the experiment with the specified parameters.

        Parameters
        ----------
        set : int (default : 1)
            set of audio files to use: 1 - files 1-12, 2 - files 13-24
            The respective files should reside in a "stimuli" subfolder of the directory of this python file.
            Within this subfolder, stimuli are organized in subfolders according to the language, e.g. "German"
        language : string
            language of the stimuli to use (default: 'German')
        """
        self.setup()
        self.setupStimuli(set, language)
        self.waitForButton('Press space to start.', ['space'])
        self.fixation.autoDraw = True
        self.processBlocks()
        self.fixation.autoDraw = False
        self.waitForButton('Finished. Press space to quit.', ['space'])
        self.finish()

    def processBlocks(self):
        """
        Process all blocks sequentially according to self.blocks. The duration and timing is either explicitly 
        specified (12 seconds for fixation) or defined by the duration of the specific wav-file. 
        """
        intactIndex = 0
        degradedIndex = 0
        
        for block in self.blocks:
            if block == 'X':
                self.wait(12)
            elif block == 'I':
                self.presentSound(self.intact[intactIndex])
                intactIndex = intactIndex + 1
            elif block == 'D':
                self.presentSound(self.degraded[degradedIndex])
                degradedIndex = degradedIndex + 1
        
    def setupStimuli(self, set, language):
        """
        Set up the list of wavefiles to use.
        
        Parameters
        ----------
        set : int
            set of audio files to use: 1 - files 1-12, 2 - files 13-24
            The respective files should reside in a folder specified when creating this instance.
            Within this folder, stimuli are organized in subfolders according to the language, e.g. "German"
        language : string
            language of the stimuli to use
        """
        
        directory =  os.path.join(self.stimuliDir, language)
        start = 1
        if(set == 2):
            start = 13

        self.intact = []
        self.degraded = []
        for n in range(start, start+12):
            self.intact.append(os.path.join(directory, str(n)+'_intact.wav'))
            self.degraded.append(os.path.join(directory, str(n)+'_degraded.wav'))

    def presentSound(self, wavfile):
        """
        Play a sound
        
        Parameters
        ----------
        wavfile : str 
            wave file to play (either absolute path or relative to the folder of the python file)
        """
        trialClock = core.Clock()
        wav = sound.Sound(wavfile, secs=-1, stereo=True, hamming=True, name="sound stimulus")
        wav.setVolume(1)
        trialDuration = wav.getDuration()
        keyb = keyboard.Keyboard()

        trialComponents = [wav]    
        self.resetTrialComponents(trialComponents)

        # reset timers
        t = 0
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
        self.thisExp.addData('wavfile', wavfile)
        self.thisExp.addData('wav.started', wav.tStart)
        self.thisExp.nextEntry()
        
        self.routineTimer.reset()

    def wait(self, time):
        """
        Wait for a specific amount of time while listening for key presses to quit the experiment.
        
        Parameters
        ----------
        time: double
            time in seconds to wait 
        """
        trialClock = core.Clock()
        trialDuration = time
        keyb = keyboard.Keyboard()

        # reset timers
        trialClock.reset()
        continueRoutine = True

        while continueRoutine:
            # get current time
            t = trialClock.getTime()
            
            # check for quit (typically the Esc key)
            if self.endExpNow or self.defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()
            
            if t > trialDuration:
                continueRoutine = False    

            # refresh the screen (needed to show the fixation cross at the beginning)
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                self.win.flip() 

        # -------Ending Routine -------
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
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED


    def waitForButton(self, message, keyList):
        """
        Wait for a button press while showing a message.
        
        Parameters
        ----------
        message : string
            message to show
        keyList : list of str
            keys to wait for
        """
        continueRoutine = True
        key_resp = keyboard.Keyboard()
        key_resp.clearEvents()

        self.message.text = message
        self.resetTrialComponents([key_resp, self.message])
        self.message.autoDraw = True
        
        while continueRoutine:
            theseKeys = key_resp.getKeys(keyList=['space'], waitRelease=False)
            if len(theseKeys):
                theseKeys = theseKeys[0]  # at least one key was pressed
                print(theseKeys)
            
                # check for quit:
                if "escape" == theseKeys:
                    self.endExpNow = True
                
                # a response ends the routine
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
        # Hide message component
        self.message.autoDraw = False
        
        
alice = AliceLocalizer()
alice.startExperiment(set, language)