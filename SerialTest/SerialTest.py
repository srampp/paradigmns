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
        self.serialPort = 'COM1'
        
    def startExperiment(self):
        self.setup()
        self.waitForSerial(3)
        self.finish()

    def setup(self):
        """
        Setup experiment info, log file and window
        """
        self._thisDir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self._thisDir)
        expName = 'SerialTest'  
        expInfo = {}
        expInfo['date'] = data.getDateStr()
        expInfo['expName'] = expName
        expInfo['psychopyVersion'] = self.psychopyVersion
        filename = self._thisDir + os.sep + u'data/%s_%s_%s' % ('test', expName, expInfo['date'])
        self.thisExp = data.ExperimentHandler(name=expName, version='',
            extraInfo=expInfo, runtimeInfo=None,
            originPath=self._thisDir + os.sep + 'SerialTest.py',
            savePickle=True, saveWideText=True,
            dataFileName=filename)
        self.logFile = logging.LogFile(filename+'.log', level=logging.EXP)
        logging.console.setLevel(logging.WARNING) 

        self.serial = serial.Serial(self.serialPort, 19200, timeout=1)

        # windowed mode for now for easier debugging
        self.win = visual.Window(
            size=(1024, 768), fullscr=False, screen=0, 
            winType='pyglet', allowGUI=False, allowStencil=False,
            monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
            blendMode='avg', useFBO=True, 
            units='height')

    def finish(self):
        """
        Clean up the experiment (close serial port, etc.).
        Output files (data, logs, etc.) are automatically handled by PsychoPy (ExperimentHandler)
        """
        self.serial.close()


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
            value = int.from_bytes(value, byteorder='big')

            # Determine here if the values constitue a signal (TODO)
            if value > 0:
                detected = detected + 1
                print(value)

            if detected >= numberOfSignals:
                continueRoutine = False
        

print('Starting...')
experiment = Experiment()
experiment.startExperiment()
