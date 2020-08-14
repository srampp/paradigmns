from PyDAQmx import *
from ctypes import *
import numpy as np
from psychopy import logging
import time

MODE_DEV = 1
MODE_EXP = 2

BUTTON_NOEVENT = 0
BUTTON_PRESSED = 1
BUTTON_RELEASED = 2

def setupTriggers(self, mode = MODE_EXP):
    print("Setup Triggers")
    if mode == MODE_DEV:
        print("Development mode")
    else:
        print("Experiment mode")
    
    # Setup triggers
    self.taskHandle = TaskHandle()
    self.read = int32()
    self.numBytes = int32()
    self.data = np.zeros((8,), dtype=np.uint8)
    self.mode = mode
            
    if self.mode == MODE_EXP:
        DAQmxCreateTask("",byref(self.taskHandle))
        DAQmxCreateDIChan (self.taskHandle, "Dev1/port2/line0:7", "", DAQmx_Val_ChanPerLine)
        DAQmxReadDigitalLines(self.taskHandle, 1, 1.0, DAQmx_Val_GroupByChannel, self.data, 8, byref(self.read), byref(self.numBytes), None)
        self.lastFMRIValue = self.data[1];
        self.button1Down = False
        self.button2Down = False
        
def startTriggers(self):
    if self.mode == MODE_EXP:
        DAQmxStartTask(self.taskHandle)
    else:
        self.lastTestTrigger = time.time()
    
def checkForFMRITrigger(self):
    if self.mode == MODE_DEV:
        now = time.time()
        if now - self.lastTestTrigger >= 2:
            self.lastTestTrigger = now
            return True
        else:
            return False
    
    trigger = False
    try:
        DAQmxReadDigitalLines(self.taskHandle, 1, 0, DAQmx_Val_GroupByChannel, self.data, 8, byref(self.read), byref(self.numBytes), None)
        if self.lastFMRIValue != self.data[1]:
            trigger = True
        self.lastFMRIValue = self.data[1]
    except DAQError as err:
        # catch timeout errors here: no data availabe and thus no triggers
        trigger = False
        print(err)
    
    return trigger
    
def checkForFMRITriggerOrResponse(self):
    if self.mode == MODE_DEV:
        now = time.time()
        if now - self.lastTestTrigger >= 2:
            self.lastTestTrigger = now
            return True, BUTTON_PRESSED, BUTTON_PRESSED
        else:
            return False, BUTTON_NOEVENT, BUTTON_NOEVENT
    
    trigger = False
    button1 = BUTTON_NOEVENT
    button2 = BUTTON_NOEVENT
    try:
        DAQmxReadDigitalLines(self.taskHandle, 1, 0, DAQmx_Val_GroupByChannel, self.data, 8, byref(self.read), byref(self.numBytes), None)
        if self.lastFMRIValue != self.data[1]:
            trigger = True
        self.lastFMRIValue = self.data[1]
        
        if self.button1Down:
            if self.data[2] == 0:
                self.button1Down = False
                button1 = BUTTON_RELEASED
        else:
            if self.data[2] == 1:
                self.button1Down = True
                button1 = BUTTON_PRESSED
        
        if self.button2Down:
            if self.data[3] == 0:
                self.button2Down = False
                button2 = BUTTON_RELEASED
        else:
            if self.data[3] == 1:
                self.button2Down = True
                button2 = BUTTON_PRESSED
    except DAQError as err:
        # catch timeout errors here: no data availabe and thus no triggers
        trigger = False
        button1 = BUTTON_NOEVENT
        button2 = BUTTON_NOEVENT
        print(err)
    
    return trigger, button1, button2

def closeTriggers(self):
    if self.taskHandle:
        DAQmxStopTask(self.taskHandle)
        DAQmxClearTask(self.taskHandle)
        
def waitForFMRITrigger(self, message):
    """
    Wait for an fMRI trigger while showing a message.
    
    Parameters
    ----------
    message : string
        message to show
    """
    continueRoutine = True
    
    self.message.text = message
    self.resetTrialComponents([self.message])
    self.message.autoDraw = True
    
    while continueRoutine:
        # check for quit (typically the Esc key)
        if self.endExpNow or self.defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        trigger = checkForFMRITrigger(self)
        if trigger:
            logging.log(level = logging.EXP, msg = 'fMRI trigger (waiting routine)')
            continueRoutine = False
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            self.win.flip()

    # -------Ending Routine "pause"-------
    # Hide message component
    self.message.autoDraw = False