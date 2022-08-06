"""StudentQueue.py - Python file that holds the functionality of the queue, which does so
via a Class structure that has a self.queue variable that holds a list of lists which
contains the student information for all students in the course. The sublists contain student
first name, last name, 95 number, email, UOID. The first four students in the queue will
be those who are 'On Deck', and are allowed to be called upon by the instructor. Once those
students have been called upon, they are removed from the front of the queue and randomly inserted
in a location in the back 70% of the queue.

Created by Michael Gao on 1-12-2022
"""

import random
#the Python random library is imported to allow queue randomization in terms of insertion and shuffling the queue
N = 30
#Predefined N is 30

class StudentQueue:

    def __init__(self, studentArray):

        """The initializer for the StudentQueue takes in an list of lists, where each
        sublist holds a student and their info (ex. student first name, student last name,
        student id, etc) of students in the course. The first four students in the queue
        will be 'On Deck'"""

        self.queue = studentArray
        #this initializes the queue to hold the contents of studentArray, which is a
        #list of lists that contains all the student information


    def numStudents(self):

        """The numStudents function returns the number of students currently
        entered into the course."""

        return len(self.queue)
        #this finds the number of lists (aka students) within the self.queue variable
        #by taking the length of it and returns it



    def getOnDeckStudents(self):
        """The getOnDeckStudents function returns the first 4 students
        in the queue, which are the 'On Deck' students."""

        return [str(self.queue[i][0] + ' ' + self.queue[i][1]) for i in range(0 , 4)]

        # this uses Python list comprehension to create and return a new list which contains a concatenated
        # string of the first and last name  of the first four students in the self.queue, which subsequently
        # are the 'On Deck' students.

        # it iterates over the values 0, 1, 2 , and 3, and takes the list at index i and then the item at the
        # 1st subindex (0) to get the first name, and the item and the 2nd subindex (1) to get the last name.
        #this then concatenates together via the string function, while adding a space between the names and
        # stores the four student names in a new list.



    def processOnDeckStudents(self, student):

        """The processOnDeckStudents function is called once an Instructor
        calls upon a student, and thus the student is removed from their
        on deck position (in the front of the queue) and moved to the back
        of the queue to allow other students to be called upon. It takes in
        a student name string as input."""


        numberStudents = self.numStudents()
        # calls the numStudents function to get the number of
        # students in the queue and assigns it to numberStudents, contains integer

        studentnames = student.split()
        # takes the student name input string and splits it based on the space
        # to distinct between first and last name. These values are stored at the 1st and
        # 2nd index location inside the studentnames array stored inside the studentnames,
        # contains string

        studentfname = studentnames[0].strip()
        # gets the first element of the studentnames array to get the first name,
        # strips any remaining whitespace, and assigns it to studentfname, contains string

        studentlname = studentnames[1].strip()
        # gets the second element of the studentnames array to get the first name,
        # strips any remaining whitespace, and assigns it to studentfname, contains string

        percentageN = N/100
        # calculates the percentage of N (defined at the top of the file) out of 100, represented as a decimal,
        # and is assigned to the variable percentageN, contains decimal

        unroundedLocation = percentageN * numberStudents
        # multiplies percentageN and numberStudents to calculate the unrounded starting index
        # of where to reinsert a called upon student, assigned to unroundedLocation, contains decimal

        startLocation = round(unroundedLocation)
        # rounds the unroundedLocation variable to the nearest whole number, contains integer

        insertionLocation = random.randint(startLocation , numberStudents)
        # chooses a random number anywhere between the startLocation and numberStudents,
        # aka the first 30% of the queue to the end of the queue (in total, the back 70% of the queue).
        # the chosen number is the specific index where the student will be inserted into the queue, contains integer


        for i in self.queue:
            #loop through the contents of the queue

            if i[0] == studentfname and i[1] == studentlname:
                self.queue.remove(i)
                self.queue.insert(insertionLocation, i)
                #if the first and last name at the specific index match the student in question, then we removed them
                # from the front of the queue and insert them in the randomly chosen location of insertionLocation
                # specified above. This inserts the student anywhere in the back 70% of the queue.
                
                break
                #break from the loop after done



    def randomize(self):
        """The randomize function randomizes the order of the students in the list."""
        random.shuffle(self.queue)
        #randomly shuffles around the order of the contents inside the self.queue variable

    def sendQueue(self):

        """The sendQueue function gets the current ordering of the student queue
        and sends it to the Student Data module in order to save the queue state."""

        return self.queue
        #this function gets the contents of the self.queue variable and returns it.


    def studentOrdering(self):

        """The studentOrdering function looks at the current ordering of the students
        in the queue."""

        for student in self.queue:
            print(student)
            #this iterates over all the sublists in the self.queue and prints all their student info.


def main():
    pass

if __name__ == "__main__":
    main()
