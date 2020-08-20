from psychopy.hardware import keyboard

import sys

sys.path.append("../Utils/")
from Triggers import (setupTriggers, closeTriggers, waitForFMRITrigger, 
                        checkForFMRITrigger, startTriggers, checkForFMRITriggerOrResponse, 
                        MODE_EXP, MODE_DEV, BUTTON_PRESSED, BUTTON_RELEASED)

# Test to check triggers and response buttons
# Run from command line or PsychoPy Experiment Runner
# The console output prints whether an fMRI trigger or a response button press/release was received
# Exit with 'escape' key
class Test:

    def __init__(self):
        setupTriggers(self, MODE_EXP)

    def close(self):
        closeTriggers(self)

    def test(self):
        keyb = keyboard.Keyboard()
        continueTest = True

        startTriggers(self)
        while(continueTest):
            trigger, button1, button2 = checkForFMRITriggerOrResponse(self)
            if trigger:
                print("fMRI trigger received")
            
            if button1 == BUTTON_PRESSED:
                print("Button 1 pressed")
            elif button1 == BUTTON_RELEASED:
                print("Button 1 released")

            if button2 == BUTTON_PRESSED:
                print("Button 2 pressed")
            elif button2 == BUTTON_RELEASED:
                print("Button 2 released")
            
            if keyb.getKeys(keyList=["escape"]):
                continueTest = False

        self.close()

test = Test()
test.test()
            
            

