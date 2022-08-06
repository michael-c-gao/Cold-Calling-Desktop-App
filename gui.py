"""
Author: JD Paul
Supporting Authors: Michael G, Ethan
Created 1/16/2022

Description:
    This file is used to build out all features of the GUI for the cold-call system. It also connects the data handling code of studentDataManager.py, fileIO.pu, and StudentQueue.py together to create
    one cohesive project

    Structure of the GUI:
        - On boot, if there is no student data, correctly formatted and saved in the cold-call software the gui will first open a file exploror that asks for a correctly formatted data file
        - After revieving a correctly formatted data file the GUI become a TK frame (aka a window built by Python's TKinter module) that is 800 px in width and 50 px in height
        - Inside the TK frame are gour InteractiveStudentWidgets (ISW) evenly spaced out using the tkinter grid system
            - Each ISW contains a string that concatonates the first and last name of a student. Each time the queue updates the keystroke event runs the code to update
            the data on the backend, and the ISW text is updated with a new students first and last name.
        - There is one drop down menu that offers functionality for uploading new student date.
            - For example: if the teacher wants to get rid of or add a new student they can edit the data file they uploaded and then upload the new data to the cold-call software
"""
import testrandom as tr
import tkinter as tk
import tkinter.font as font
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import fileIO as fio  # key_bindings function() returns keybindings as a dictionary
from studentDataManager import StudentDataManager as SDM
from StudentQueue import StudentQueue

class InteractiveStudentWidget(tk.Label):
    """
    **NOTE: This class must be placed above MainWin because MainWin takes this class as a type for one of its methods**
    This class will display the students name in a box. It will be instantiated four times and take up one quarter
    of the rootWindow space. Once all four InteractiveStudentWidget are instantiated they will fill the rootWindow from
    left to right
    """

    def __init__(self, masterWindow, width, studentName, font, row=0, column=0, height=50):
        """
        masterWindow will be the root window in which the student will be placed
        studentData will be the data provided from the input file
        """
        # Using a StringVar so we can update the names in the slot
        # Source: https://www.delftstack.com/howto/python-tkinter/how-to-change-the-tkinter-label-text/
        self.text = tk.StringVar()
        self.text.set(studentName)
        # using a variable to fill in the name. Also adding a border with borderwidth and relief.
        tk.Label.__init__(self, masterWindow, textvariable=self.text, font=font, borderwidth=1,
                          relief="solid", width=width - 2, height=height - 2, bg='black', fg='white')
        self.grid(row=row, column=column)

    def setName(self, name: str):
        self.text.set(name)


class MainWin(tk.Tk):
    def __init__(self, maxNumberStudents):
        # Call parent initializer
        super().__init__()

        # Set the header of the window
        self.title("Cold Calling")

        # Set the window color
        self.configure(bg='lightgray')

        # Set up the grid system so everything is equal when spacing. Source: https://www.pythontutorial.net/tkinter/tkinter-grid/
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        # Make the window sit on top of all other windows Source: https://www.tutorialspoint.com/how-to-put-a-tkinter-window-on-top-of-the-others
        self.attributes('-topmost', True)

        # Set and save the data to keep track of how many students are in the window.
        self.maxNumberStudents: int = maxNumberStudents
        self.numberOfStudent = 0

        # Set the width of each student entry (ex. if there are 4 students in the window and the width of the window is 800 px then the width
        # of each  student entry will be 200 px). Pass the value in when building IndteractiveStudentWidgets.
        # self.widthOfStudentEntry = int(winWidth / maxNumberStudents)
        self.widthOfStudentEntry = int(800 / maxNumberStudents)

        self.updateWindowLocation()

        # Set the size of the window with pixel values
        self.geometry("800x50")

        # the first time the program is run,
        # init the student database and import the photos
        if not fio.data_exists():
            #print("calling init database")
            self.init_database()
        #print("now past init database")
        # Fonts
        self.times24 = font.Font(family="Times", size=14)

        self.row = 0  # This MUST stay constant

        # Each spot will have its text edited with a students name in its place
        self.firstSpot = InteractiveStudentWidget(self, 200, "0 0", self.times24, row=self.row, column=0)
        self.secondSpot = InteractiveStudentWidget(self, 200, "1 1", self.times24, row=self.row, column=1)
        self.thirdSpot = InteractiveStudentWidget(self, 200, "2 2", self.times24, row=self.row, column=2)
        self.fourthSpot = InteractiveStudentWidget(self, 200, "3 3", self.times24, row=self.row, column=3)

        # Set the current student for key binding purposes
        self.currentStudent = None

        self.PathToStudentData = ""
        self.PathToStudentImages = None

        # Setup key bindings
        self.kbDictionary = fio.key_bindings()
        self.count = 0

        # Load the queue of students. If there are none loaded then procede to load the data
        self.studentqueue = None
        if fio.data_exists():
            # Call to load the roster data from SDM
            SDM.LoadRoster(fio.load_queue())
            # Set the studentqueue property for this class
            self.studentqueue = StudentQueue(fio.load_queue())
            # create a temporary variable which stores a list of the first four students in the queue
            studentlist = self.studentqueue.getOnDeckStudents()
            
            # Fill the four GUI spots with the first four names that were saved in studentlist
            self.firstSpot.setName(studentlist[0])
            self.secondSpot.setName(studentlist[1])
            self.thirdSpot.setName(studentlist[2])
            self.fourthSpot.setName(studentlist[3])

        # Map the correct keys to the correct functions
        for key in self.kbDictionary:
            if key == "right":
                self.bind(self.kbDictionary[key], self.right)
            elif key == "left":
                self.bind(self.kbDictionary[key], self.left)
            elif key == "remove":
                self.bind(self.kbDictionary[key], self.remove)
            elif key == "flag":
                self.bind(self.kbDictionary[key], self.flag)
            #print(f"key {key} contains value {self.kbDictionary[key]}")
        
        # bind control+t so the user can test the normal distribution of students by writing 100 removes from 100 queue randomizations to the daily_log.txt file
        self.bind('<Control-t>', self.testData)
        
        # instantiate the menu bar that contains an import option to import new student roster data
        self.createMenuBar()

    def testData(self, event):
        '''
        This is the event handler for the key press combination of Control+t for testing 100 remove operations on 100 randomized order variations of the currently stored student queue.
        '''
        # Ask the user if they are sure they want to perform the test which would write 10,000 new lines to their daily_logs.txt file
        yesno = tk.messagebox.askyesno("ARE YOU SURE",
                                      "If you run this test it will write 10 thousand lines to your daily files. Are you sure you want to run this test?")
        if yesno is False:
            # do not perform the test if the user says no to wanting to perform it
            return
        
        # Run the test becasue the user confirmed they want to run it
        tr.Main()

    def updateWindowLocation(self):
        # Move window centered horizontally and at the top of the window.
        # Source: https://www.foxinfotech.in/2018/09/how-to-create-window-in-python-using-tkinter.html
        winWidth = self.winfo_reqwidth()
        posRight = int(self.winfo_screenwidth() / 2 - winWidth / 2)
        posDown = 0  # puts the window at the top of the screen
        self.geometry("+{}+{}".format(posRight, posDown))

    # Keyboard functions
    def right(self, event):
        '''
        This method is called when the user clicks on the right arrow key, or the key they specified in the config file for moving right:
        There are two cases for what this method will do:
            if there are no currently highlighted students on the deck window then this method will highlight the right most student
            otherwise this method will move the highlighting of a student one spot to the right of itself or not at all if the rightmost student is already highlighted
        '''
        #print("right key pressed")
        if self.currentStudent is None:
            self.currentStudent = self.fourthSpot
            self.fourthSpot.configure(bg='white', fg='black')
        elif self.currentStudent == self.firstSpot:
            self.firstSpot.configure(bg='black', fg='white')
            self.secondSpot.configure(bg='white', fg='black')
            self.currentStudent = self.secondSpot
        elif self.currentStudent == self.secondSpot:
            self.secondSpot.configure(bg='black', fg='white')
            self.thirdSpot.configure(bg='white', fg='black')
            self.currentStudent = self.thirdSpot
        elif self.currentStudent == self.thirdSpot:
            self.thirdSpot.configure(bg='black', fg='white')
            self.fourthSpot.configure(bg='white', fg='black')
            self.currentStudent = self.fourthSpot

    def left(self, event):
        '''
        This method is called when the user clicks on the left arrow key, or the key they specified in the config file for moving left:
        There are two cases for what this method will do:
            if there are no currently highlighted students on the deck window then this method will highlight the left most student
            otherwise this method will move the highlighting of a student one spot to the left of itself or not at all if the leftmost student is already highlighted
        '''
        #print("left key pressed")
        if self.currentStudent is None:
            self.currentStudent = self.firstSpot
            self.firstSpot.configure(bg='white', fg='black')
        elif self.currentStudent == self.fourthSpot:
            self.fourthSpot.configure(bg='black', fg='white')
            self.thirdSpot.configure(bg='white', fg='black')
            self.currentStudent = self.thirdSpot
        elif self.currentStudent == self.thirdSpot:
            self.thirdSpot.configure(bg='black', fg='white')
            self.secondSpot.configure(bg='white', fg='black')
            self.currentStudent = self.secondSpot
        elif self.currentStudent == self.secondSpot:
            self.secondSpot.configure(bg='black', fg='white')
            self.firstSpot.configure(bg='white', fg='black')
            self.currentStudent = self.firstSpot

    def createMenuBar(self):
        '''
        Creates the menu bar at the top of the desktop window for Mac computer or at the top of this window for Windows and Linux users.

        There is one menu on the bar:
            An import menu with one option:
                The option is to import new student data (as in a new roster). This button will cause a file picker to open and prompt for a new data file. The user can either cancel or pick a new,
                correctly formatted, student roster file. After picking the new file, assuming it is formatted correctly, the program asks if the user is sure they want to overwrite the currently
                loaded student roster file. If the user says yes, then the program replaces the current data file with the new one and updates the data in all nessasary places.
        '''
        # Add menu options Source: https://www.pythontutorial.net/tkinter/tkinter-menu/
        # create a menubar
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        # create a menu
        self.importMenu = tk.Menu(self.menubar)

        # add a menu item to the menu
        self.importMenu.add_command(
            label="Import Student Data",
            command=self.pick_new_database
        )

        # add the File menu to the menubar
        self.menubar.add_cascade(
            label="Import",
            menu=self.importMenu
        )

    def remove(self, event):
        '''
        Event handler for the remove key which is the up arrow by default.
        This method checks if there is a student highlighted. If so, it removes the student from all nessasary locations in the program and logs them to the nessasary log files. It then updates the
        student queue and updates the gui so that it displays the new newtudent and moves the other three left to the left. Notably, this method does NOT flag the removed student in log files.
        '''
        #print("remove key pressed")
        if self.currentStudent is not None:
            self.currentStudent.configure(bg='black', fg='white')
            student = self.currentStudent.cget('text')

            # give the student name to the queue to be taken off
            self.studentqueue.processOnDeckStudents(student)

            # give the student name and flagged value, by first getting their id in Ethans code
            studentList = student.split()
            studentUid = SDM.GetStudentUid(studentList[0], studentList[1])
            fio.log_cold_call(studentUid, flagged=False)

            # call for the new first four names in the queue
            studentlist = self.studentqueue.getOnDeckStudents()

            # update the names of the gui "on deck" display
            self.firstSpot.setName(studentlist[0])
            self.secondSpot.setName(studentlist[1])
            self.thirdSpot.setName(studentlist[2])
            self.fourthSpot.setName(studentlist[3])

            # Save the data state
            fio.save_queue(self.studentqueue.sendQueue())

        self.currentStudent = None

    def flag(self, event):
        '''
        Event handler for the remove key which is the up arrow by default.
        This method checks if there is a student highlighted. If so, it removes the student from all nessasary locations in the program and logs them to the nessasary log files. It then updates the
        student queue and updates the gui so that it displays the new newtudent and moves the other three left to the left. Notably, this method DOES flag the removed student in log files.
        '''
        #print("flag key pressed")
        if self.currentStudent is not None:
            self.currentStudent.configure(bg='black', fg='white')
            self.currentStudent.configure(bg='black', fg='white')
            student = self.currentStudent.cget('text')

            # give the student name to the queue to be taken off
            self.studentqueue.processOnDeckStudents(student)

            # give the student name and flagged value, by first getting their id in Ethans code
            studentList = student.split()
            uid = SDM.GetStudentUid(studentList[0], studentList[1])
            fio.log_cold_call(uid, flagged=True)

            # call for the new first four names in the queue
            studentlist = self.studentqueue.getOnDeckStudents()

            # update the names of the gui "on deck" display
            self.firstSpot.setName(studentlist[0])
            self.secondSpot.setName(studentlist[1])
            self.thirdSpot.setName(studentlist[2])
            self.fourthSpot.setName(studentlist[3])

            # Save the data state
            fio.save_queue(self.studentqueue.sendQueue())

        self.currentStudent = None


    def select_file(self):
        # Source: https://www.pythontutorial.net/tkinter/tkinter-open-file-dialog/
        filename = fd.askopenfilename(
            title='Open a student roster text file',
            initialdir='~'
        )
        return filename

    # More Files Input: JD and Sam
    # Runs the first time the program starts
    def init_database(self):
        '''
        This method is called by the initializing method of this class when the data file under ./data/students is not found to exist. If the file doe snot exist this methods opens a file picker
        window and asks for a correctly formatted student data file until one is picked by the user
        '''
        selectedFilePath = self.select_file()
        #print(f"The selected file path for the database is {selectedFilePath}")
        error = fio.import_student_data(path=str(selectedFilePath))
        
        while error != 0:
            # if file already exists
            # this should never happen becasue init won't get called if there is a database loaded already

            if error == 3:
                # if the user hits cancel
                showinfo(
                    title="Error!",
                    message="You must pick a file. Format is: tab deliminated text file where hte order of data is First name, last name, 961 number, emial, perfered name"
                )
            elif error == 1:
                showinfo(
                    title="Error!",
                    message="Student data already exists!"
                )
            # if file doesn't match the correct format
            elif error == 2:
                showinfo(
                    title="Error!",
                    message="File is not in the correct format! It must be in a tab/comma deliminated text file where the order of data is First name, last name, 951 number, email, perfered name"
                )
            selectedFilePath = self.select_file()
            error = fio.import_student_data(path=str(selectedFilePath))

        SDM.LoadRoster(fio.load_queue())
        self.studentqueue = StudentQueue(fio.load_queue())
        self.studentqueue.studentOrdering()
        self.PathToStudentData = selectedFilePath

    def pick_new_database(self):
        '''
        This method is called by the createMenuBar() method when the option to import student data is selected by the user. This method allows the user to pick a new file from there computer with
        updated student data. Perhaps the teacher had a student drop the class or they are teaching a new term, meaning new students. If either of those senarios were true the teacher could use the
        button this method is attatched to to add new students.

        This method works by opening a file picker view and prompting the user for a new data file or to cancel, in which case the user would go back to using there original data. The user will be
        prompted for a file until a correctly formatted file is chosen by the user or they decide to cancel the operation.
        '''
        selectedFilePath = self.select_file()

        #print(f"The selected file path for the updated database is {selectedFilePath}")
        error = fio.import_student_data(path=str(selectedFilePath), over_write=True)
        if selectedFilePath == "":
            # then the user hit cancel
            return

        while error != 0:
            if selectedFilePath == "":
                # then the user hit cancel
                return

            # if file already exists
            if error == 1:
                yorn = tk.messagebox.askyesno("Are you sure",
                                              "Student data is already loaded into the program. Are you sure you want to overwrite it?")
                if yorn is True:
                    error = 0
            # if file doesn't match the correct format
            elif error == 2:
                rorc = tk.messagebox.askretrycancel("Wrong Format",
                                                    "The data is not formatted correctly. Do you want to retry?")
                if rorc is False:
                    fio.import_student_data(path=self.PathToStudentData)
                    fio.save_images(path=self.PathToStudentImages)
                    return
            selectedFilePath = self.select_file()
            error = fio.import_student_data(path=str(selectedFilePath), over_write=True)

        # Save the new path values
        SDM.LoadRoster(fio.load_new_queue())
        self.studentqueue = StudentQueue(fio.load_new_queue())
        self.studentqueue.studentOrdering()
        self.PathToStudentData = selectedFilePath

        # reset the GUI "deck"
        studentlist = self.studentqueue.getOnDeckStudents()

        self.firstSpot.setName(studentlist[0])
        self.secondSpot.setName(studentlist[1])
        self.thirdSpot.setName(studentlist[2])
        self.fourthSpot.setName(studentlist[3])
 
