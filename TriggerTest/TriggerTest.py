from PyDAQmx import *
import numpy
from ctypes import *

# Test the response and fMRI trigger signals
# The Neurospec box outputs digital boolean signals on 8 lines (i.e. 8x yes/no)
# The NIDAQmx driver uses a device name to address the box, which can be changed
# in the NIDAQ software. Default is "Dev1", which is used here. The DB25 port on the box
# is port 2, resulting in the complete device/port-name "Dev1/port2/line0:7", i.e. currently
# we read all 8 lines. 
# The test script runs continuously and outputs button presses and releases, as well as fMRI triggers.
# Button 1 is on pin 3, button 2 on pin 4 (or zero-based 2 and 3).
# The fMRI trigger flips lines 2 and 5 (or zero-based 1 and 4)
# Exit the program with CTRL-C. This might work better outside of PsychoPy, e.g. from the command line
# (python TriggerTest.py in the directory of this file)

# Installing PyDAQmx
# The easiest and cleanest way is probably to install both psychopy and PyDAQmx into a common
# python installation, using a dedicated environment, e.g. using Anaconda
# - Install Anaconda (free individual edition, Python 3.8, Win 64bit works): https://www.anaconda.com/products/individual
# - Download the PsychoPy environment file: https://www.psychopy.org/download.html#conda
# - Open a terminal, go to the folder with the environment file and execute: conda env create -n psychopy -f psychopy-env.yml
# - Activate the PsychoPy environment on the command line: conda activate psychopy
# - Install PyDAQmx: pip install PyDAQmx
# - Start PsychoPy from the command line: psychopy

# Declaration of variable passed by reference
taskHandle = TaskHandle()
read = int32()
numBytes = int32()
data = numpy.zeros((8,), dtype=numpy.uint8)

try:
    # DAQmx Configure Code
    DAQmxCreateTask("",byref(taskHandle))
    DAQmxCreateDIChan (taskHandle, "Dev1/port2/line0:7", "", DAQmx_Val_ChanPerLine)

    # DAQmx Start Code
    DAQmxStartTask(taskHandle)

    # DAQmx Read Code
    #DAQmxReadAnalogF64(taskHandle,1000,10.0,DAQmx_Val_GroupByChannel,data,1000,byref(read),None)
    button1_down = False
    button2_down = False
    fMRIPrevious1 = False
    fMRIPrevious4 = False

    # Read the current input once to get the current state of the fMRI trigger
    DAQmxReadDigitalLines(taskHandle, 1, 10.0, DAQmx_Val_GroupByChannel, data, 8, byref(read), byref(numBytes), None)
    fMRIPrevious1 = data[1]
    fMRIPrevious4 = data[4]

    while(True):
        DAQmxReadDigitalLines(taskHandle, 1, 10.0, DAQmx_Val_GroupByChannel, data, 8, byref(read), byref(numBytes), None)
        if data[2] == 0:
            if not button1_down:
                button1_down = True
                print("Button 1 pressed")
        else:
            if button1_down:
                button1_down = False
                print("Button 1 released")    

        if data[3] == 0:
            if not button2_down:
                button2_down = True
                print("Button 2 pressed")
        else:
            if button2_down:
                button2_down = False
                print("Button 2 released") 

        if data[1] != fMRIPrevious1:
            fMRIPrevious1 = data[1]
            print("fMRI trigger on line 2: " + str(data[1]))

        if data[4] != fMRIPrevious4:
            fMRIPrevious4 = data[4]
            print("fMRI trigger on line 5: " + str(data[4]))

except DAQError as err:
    print("DAQmx Error: %s"%err)
finally:
    if taskHandle:
        # DAQmx Stop Code
        DAQmxStopTask(taskHandle)
        DAQmxClearTask(taskHandle)