'''
Author: JD Paul
Created 1/20/2022

Description:
    This file acts as the starting point to the cold-calling software. After running this file
    in the command: "python3 main.py" it starts the sequence of code that sets up the entire program.
'''

import tkinter as tk
from gui import MainWin

class Main():
    '''
    This class is instantiated at the bottom of this file every time the application is run 
    using hte command: 
        python3 main.py 
    In order to work correctly this file must be paired in the same directory as the files: 
        gui.py
        fileIO.py
        StudentQueue.py
        studentDataManager.py
    And the directory structure relative to the directory this file lives in as:
        data/logs (ie. a data directory in the same directory as this file and a logs
        directory in the data directory)
    Once run, this file instantiates its Main class which creates the main window and
    runs the programs mainloop.
    '''
    def __init__(self):
        '''
        This initializer starts the sequence of events to boot and run the cold-call
        software. This class creates a window with 4 students and then runs the mainloop
        used by tkinter. That sets off the chain of events that gets the software to run
        correctly.
        '''
        self.rootWindow = MainWin(4)  # 4 is the maximum number of students in the window

        # Run the window mainloop so it shows up on screen
        self.rootWindow.mainloop()

if __name__ == "__main__":
    Main()
