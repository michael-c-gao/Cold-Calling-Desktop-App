"""testrandom.py - Python file that implements the random distribution testing
of student queue selection by instantiating 100 different queues and randomly cold
calling 100 students within each of the queues. The called-upon students will be logged in
the daily_log.txt file.

Created by Michael Gao, JD Paul on 1-25-2022
"""

from StudentQueue import *
from studentDataManager import StudentDataManager as SDM
import fileIO as fio
import os.path, os

def Main():

    """This program instantiates 100 different queues, and within each of the 100 queues
        it randomly chooses one of the on deck students and then logs those students in the daily_logs.txt
        This leads to 10000 total randomly called upon students for random distribution analysis if the user
        chooses to do so.
        """

    if not os.path.exists('./data/students'):
        return 'There is no data to test! Please run the program and upload data first.'
        #this checks if the path data/students exists or not, aka whether there exists student
        # data or not. If so, it returns a message to the user to upload student data.


    for i in range(0,100):
        #iterates 100 times, from 0 - 99

        SDM.LoadRoster(fio.load_queue())
        #loads the student data
        stud = StudentQueue(fio.load_queue())
        # instantiates a StudentQueue object stud and passes in the processed student queue data
        stud.randomize()
        # randomizes the ordering of the queue

        for j in range(0,100):
            # iterates 100 times, from 0 - 99

            randomlychosenstudent = random.randint(0, 3)
            # chooses a random integer between 0 and 3 (i.e. 0, 1, 2, 3) and assigns it to
            # randomlychosenstudent variable

            student = stud.queue[randomlychosenstudent]
            # selects the student and their information by indexing into the stud.queue via
            # the randomlychosenstudent variable and assigns it to student variable, holds a list

            studentname = student[0] + ' ' + student[1]
            # creates the student name by concatenating the student first name, stored in student[0],
            # with a space via ' ', then the student last name, stored in student[1], into the studentname
            # variable, holds a string

            stud.processOnDeckStudents(studentname)
            # calls the processOnDeckStudents with the studentname parameter to remove the student from
            # the front of the queue and randomly insert it anywhere in the back 70% of the queue

            studentUid = SDM.GetStudentUid(student[0], student[1])
            # generate the studentUid by calling the GetStudentUid with the student first and last name,
            # stored inside student[0] and student[1] respectively

            fio.log_cold_call(studentUid, flagged=False)
            #log the student in the cold call participation log via the studentUid with no flag.


if __name__ == '__main__':
    Main()
