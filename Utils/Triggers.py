from PyDAQmx import *
from ctypes import *
import numpy as np
from psychopy import logging
import time

MODE_DEV = 1
MODE_EXP = 2

def setupTriggers(self, mode = MODE_EXP):
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
    
    return trigger

def closeTriggers(self):
    if self.taskHandle:
        DAQmxStopTask(taskHandle)
        DAQmxClearTask(taskHandle)
        
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