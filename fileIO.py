"""
Authors: Sam Gebhardt, Ethan Killian

Read and write to files that store student data.
Read files for importing data.
    * Inital import of student data
    * Re importing student data
    * Saving and reading the queue
    * Loading default controls

Write to export data.
    * Exporting student data
    * Log any cold calls in log files
    * Export final Participation

"""
import email
import os.path, os
import datetime
import shutil
import re
from studentDataManager import StudentDataManager as SDM

# Student data is seperated by either a tab or comma
DELIMITER = "\t"
# DELIMITER = ","


def data_exists() -> bool:
    """
    Check if the student data has 
    already been imported into the system.
    
    Parameters:

    None

    Returns Bool
    True -> The data exists
    False -> The data doesn't exist
    """
    
    # Check the path where the student data would be 
    if os.path.exists("./data/students"):
        return True

    return False


def import_student_data(path="", over_write=False) -> int:
    """
    Take a file with tab seperated values and save it as user values.
    File must be in the correct format. If a file already exists, then
    warn the user of override.

    The inputed data is in the following format:
    <first name> <tab> <last name> <tab> <UO ID> <tab> <email address>

    or

    <first_name> <tab> <last_name> <tab> <UO ID> <tab> <email_address> <tab>
    <phonetic_spelling> <tab> <reveal_code> <newline>

    Saves the student data in program_dir/data/students
    
    Parameters:

    path: str -> The path to import student data from
    over_write: bool -> If set to True any current data is overwritten by new data

    Return: int
    0 -> No error
    1 -> Student Data already exists
    2 -> File in incorrect format
    3 -> No path was selected by the user
    """

    # If there is already data in the system, then return error 1 to the gui
    if data_exists():
        # If over_write is false return error, otherwise continue
        # This allows the user to reimport student data
        if not over_write:
            return 1  # error
    
    # If no path was selected by the user, then return error 3 to the gui
    if path == "":
        return 3

    # A list to store the student information as it's
    # read in from disk
    students = []
    
    # Open the path supplied from the gui
    # f is the file object
    with open(path, "r") as f:

        # The regex pattern to match against the student data as it's read in
        # The delimiter alters the pattern by switching between a comma and tab
        # The patterns are hard coded because tabs require raw strings, thus
        # formatted strings can't be used
        pattern = r"[A-z\-]+,[A-z\-]+,[0-9]{9},[A-z0-9]+@uoregon.edu"
        if DELIMITER == "\t":
            pattern = r"[A-z\-]+\t[A-z\-]+\t[0-9]{9}\t[A-z0-9]+@uoregon.edu"

        
        # for each line in the file
        # i is each line in the file
        for i in f:

            # Make sure the line from the file matches the regex, return error if it doesn't
            if not re.match(pattern, i):
                return 2

            # split the line on the delmiter
            i = i.split(DELIMITER)

            # If the data doesn't have phonetic spelling, add the first name as the 
            # phonetc spelling
            if len(i) == 4:
                i.append(i[0])

            # Append the position for the reveal code
            i.append("")

            # Append the individual student data to the overall list
            students.append(i)

    # for each student in the list of students
    # i is a list of student information
    for i in students:

        # for each element in the list remove any whitespace
        # j is an iterator over the length of the list to access each element
        for j in range(len(i)):

            # update the student information without whitespace
            i[j] = i[j].strip()

    # for each student in the list of students
    # student is a student in the master list of students
    for student in students:

        # get the unique student ID of the specific student
        uid = SDM.GetStudentUid(student[0], student[1])

        # create an list filled with None of size 6
        roster_data = [None for i in range(6)]

        # Copy the student list into the roaster data list
        roster_data[0:] = student[:]

        # Add the student to the roaster data
        SDM.StudentRoster[uid] = tuple(roster_data)

    # Create the student file to store the newly read in data
    # f is the file object
    with open("./data/students", "w") as f:
        
        # for each student in the list of students
        # i is a list of student information for a specific student
        for i in students:

            # formated is the string that will be written to the new file
            # It will contain all the student data seperated by the correct delimiter
            formated = ""

            # for each piece of information for the student add it 
            # to the formatted str
            # j is an iterator for the length of the list minus 1
            for j in range(len(i) - 1):
                formated += i[j] + DELIMITER
            
            # add a newline at the end
            formated += "\n"
            # write the formatted string to the new file
            f.write(formated)

    # return no error to the gui
    return 0


def save_queue(queue: list) -> None:
    """
    Public interface to save the current ordering of the queue. Is called
    each time a student is removed from the queue.
    
    Parameters:

    queue: list -> A list of lists. The outer list is a list of students. The inner
        list is a list of information about the student. Name, UO ID, Email, Phonetic Spelling

    Return: None
    """

    # Open the file that contains the persistant ordering of the queue
    # f is a file object
    with open("./data/queue_order", "w") as f:
        
        # for each student in the queue
        # i is a list of student information
        for i in queue:

            # formated is the string that will be written to the new file
            # It will contain all the student data seperated by the correct delimiter
            formated = ""
            
            # for each piece of information for the student add it 
            # to the formatted str
            # j is an iterator for the length of the list minus 1
            for j in range(len(i) - 1):
                formated += i[j] + DELIMITER

            # add a newline at the end
            formated += "\n"
            
            # write the formatted string to the new file
            f.write(formated)


def load_queue() -> list:
    """
    Public interface for queue.py that loads the saved state of the queue into memory
    at the start of the program. Returns a list of lists of student names.
    
    Parameters:

    None

    Return: list
        
        A list of lists. The outer list is a list of students. The inner
        list is a list of information about the student. Name, UO ID, Email, Phonetic Spelling
    """

    # students is the list that will hold all the student information
    students = []

    # Path is the path that will be opened to read the queue ordering
    # There are two possible paths: One for the first time the program runs, where
    # it just loads the student data in the order it was read in. The other path
    # is the default saved queue file.
    path = "./data/queue_order"

    # if the queue order doesn't exist, then just init from students
    if not os.path.exists("./data/queue_order"):
        path = "./data/students"

    # Open the correct folder
    # f is a file object
    with open(path, "r") as f:

        # for each line in the file
        # i is a line from the file
        for i in f:

            # split the line based on the set delimeter
            i = i.split(DELIMITER)

            # for each element in the list remove any whitespace
            # j is an iterator over the length of the list to access each element
            for j in range(len(i)):

                # update the student information without whitespace
                i[j] = i[j].strip()

            # append the whitespace free data to the list of students
            students.append(i)

    # return the list of students to the gui
    return students


def load_new_queue() -> list:
    """
    Public interface for queue.py that loads the saved state of the queue into memory
    at the start of the program. Returns a list of lists of student names.
    The difference between this and load_queue is the function is called if the user imports new student data
    during the execution of the program.

    Parameters:

    None

    Return: list

        A list of lists. The outer list is a list of students. The inner
        list is a list of information about the student. Name, UO ID, Email, Phonetic Spelling
    """

    students = []
    with open("./data/students", "r") as f:

        # for each line in the file
        # i is a line from the file
        for i in f:

            # split the line based on the set delimeter
            i = i.split(DELIMITER)

            # for each element in the list remove any whitespace
            # j is an iterator over the length of the list to access each element
            for j in range(len(i)):

                # update the student information without whitespace
                i[j] = i[j].strip()

            # append the whitespace free data to the list of students
            students.append(i)

    # return the list of students to the gui
    return students


def key_bindings() -> dict:
    """
    Check if a config file is provided that overrides the default controls.
    Otherwise, return the defualt controls.

    Parameters:

    None

    Return: dict

        A dictonary that holds the controls for the program.
    """

    # default_controls[action] = key on keyboard
    # default_controls["right"] = right arrow
    # default_controls["left"] = left arrow
    # default_controls["up"] = up arrow
    # default_controls["down"] = down arrow

    # A dict that holds the default controls for the program
    default_controls = {
        "right": "<Right>",
        "left": "<Left>",
        "remove": "<Up>",
        "flag": "<Down>"
    }

    # if the config file doesn't exist of its empty just return the default controls
    if not os.path.exists("./data/config") or os.path.getsize("./data/config") == 0:
        return default_controls

    # a dict that holds the custom controls provided by the user
    custom_controls = {}

    # file must be formated as: <action> : <key>
    # open the config file
    # f is the file object
    with open("./data/config", "r") as f:

        # for each line in the file
        # i is the line in the file
        for i in f:

            # split each line on the colon character
            i = i.split(":")

            # add the custom control to the dict
            custom_controls[i[0].strip()] = i[1].strip()

    # return the custom controls
    return custom_controls


def export_student_data(exp_path: str) -> None:
    ''' Create a file that has the student info in the correct format.
    '''

    def get_roster_export_lines():
        ''' An internal generator function used to build each line for the exported data.

        Yields
        ------
        str: A line for each student containing all of their data separated by the delimiter.
        '''

        # Iterate over every student in the student roster.
        # For each student, use their unique identifier to fetch their data from the roster.
        # Then build and yield a string containing all of their student data separated by the delimiter.
        for uid in SDM.StudentRoster:
            student_data = SDM.StudentRoster.get(uid)
            yield DELIMITER.join(student_data)

    # If we try to export to a path that already exists we return an error to prevent overwriting potentially critical files.
    if os.path.exists(exp_path):
        raise KeyError("Attempted to export roster data to a preexisting file. This is not allowed.")


    # Open the target file and write the data for the current student roster to it.
    with open(exp_path, 'w') as exp_file:
        # Write the header containing the title for each data entry separated by the delimiter.
        exp_file.write(f"{DELIMITER.join(('<First Name>', 'Last Name', 'UOID', 'email', 'Phonetic Spelling', 'Reveal Code'))}\n")
        # Write the entries for each student on separate lines.
        exp_file.writelines(get_roster_export_lines())


def log_cold_call(uid: str, flagged: bool = False) -> None:
    """
    Takes the reponse of the student along with their name and
    logs it in the daily log file.

    Parameters
    ----------
    uid (str): The unique identifier of the student that was cold called.
    flagged (bool): Whether the student's cold call was flagged by the instructor.
    """

    # Get the data for the selected student.
    student_data = SDM.StudentRoster.get(uid, None)
    # If there is no data for the student the student does not exist and we throw an error.
    if student_data is None:
        raise KeyError("The student does not exist on the roster.")

    # Get the current time from the users computer.
    now = datetime.datetime.now()
    # Split the current time into the current date and the current time of day.
    date, time = now.date().strftime('%Y/%m/%d'), now.time().strftime('%H:%M:%S')
    # Distribute the data for the current student to variables to make it easier to insert the date and time into the logs.
    fname, lname, uoid, email, phonetic, reveal_code = student_data[0:6]

    # 
    needs_header = False
    # Check whether the log file already exists.
    if not os.path.exists('./data/logs/daily_logs.txt'):
        # If it doesn't we need to make a header file.
        needs_header = True

    # Open the logging file and begin appending to it.
    with open('./data/logs/daily_logs.txt', 'a') as logfile:
        # If the file needs a header, we add one.
        if needs_header:
            logfile.write(f"{DELIMITER.join(('<Date>', '<Time>', '<Flagged>', '<First Name>', '<Last Name>', '<UOID>', '<Email>', '<Phonetic Spelling>', '<Reveal Code>'))}\n")
        
        # Append the text for the new log to the end of the file.
        logfile.write(
            f"{DELIMITER.join((date, time, str(flagged), fname, lname, uoid, email, phonetic, reveal_code))}\n")


def export_final_participation(exp_path: str):
    """ Compiles the existant student logs into a compiled record of how student performed in the class.

    Arguments
    ---------
    exp_path (str): The filepath to export these logs to.

    Raises
    ------
    KeyError: When we attempt to export to a file that already exists.
    """

    def load_daily_logs():
        """ An internal function responsible for importing the data from the existing logging file.
        """

        # Initialize a variable to hold the contents of the logs file.
        # Must be done outside of the 'with' block allow other parts of the proc to access it.
        logs = None
        # Open the logging file to read from.
        with open('./data/logs/daily_logs.txt', 'r') as logfile:
            # Skip the header line on the logs.
            logfile.readline()
            #Store the rest of the logfiles data.
            logs = logfile.readlines()

        # If there is no data there were no logs and we should't bother.
        if logs is None:
            return

        # for each log entry in the log file...
        for log in logs:
            # Convert the entry from a single, monolithic, string to a set of parameters.
            logdata = [datum.strip() for datum in log.split()]
            # Parse whether or not the log entry was flagged to a bool.
            logdata[2] = bool(logdata[2])
            # Yield the resulting log parameters.
            yield tuple(logdata)

    def compile_final_participation_logs():
        """ Internal function responsible for generating the final participation logs.
        """

        class ParticipationData:
            """ An internal class holding the participation data for a student.

            Attributes
            ----------
            fname (str): The first name of the student
            lname (str): The last name of the student.
            uoid (str): The university id of the student.
            email (str): The email address for the student.
            phonetic (str): The phonetic spelling of the students name.
            reveal_code (str): The reveal code for the student.
            dates (List[str]): The dates the student was cold called.
            times_flagged (int): The number of times this student has been flagged while this logfile has been active.
            """

            def __init__(self, fname=None, lname=None, uoid=None, email=None, phonetic=None, reveal_code=None):
                # Set student attributes as given.
                self.fname, self.lname, self.uoid, self.email, self.phonetic, self.reveal_code = fname, lname, uoid, email, phonetic, reveal_code
                # Create an empty list to hold the dates the student was cold called.
                self.dates = []
                # Create an accumulated to hold the number of times the student was flagged when the student was cold called.
                self.times_flagged = 0

            def __str__(self) -> str:
                # Parse this entry into its component parts for exporting.
                return DELIMITER.join((
                    len(self.dates),
                    self.times_flagged,
                    self.fname,
                    self.lname,
                    self.uoid,
                    self.phonetic,
                    self.reveal_code,
                    f"[{', '.join(self.dates)}]"
                ))

        # Create a dictionary to store the cumulative participation info for each student.
        students = {}

        # For each log that this program has ever logged.
        for log in load_daily_logs():
            # Get the unique identifier of the student that was logged.
            uid = SDM.GetStudentUid(log[3], log[4])

            # Attempt to fetch the cumulative participation info for this student.
            participation = students.get(uid, None)
            if participation is None:
                # If we don't already have one see if we can build one from the current student roster.
                roster_data = SDM.StudentRoster.get(uid, None)
                # Otherwise, just use the data from the log.
                if roster_data is None:
                    roster_data = tuple(log[3:])

                # Create and store a brand new participation log entru.
                participation = ParticipationData(roster_data[0], roster_data[1], roster_data[2], roster_data[3],
                                                roster_data[4], roster_data[5])
                students[uid] = participation

            # Append the date of the current cold call log to the students participation data.
            participation.dates.append(log[0])
            if log[2]:
                # Also add whether the student was flagged to the accumulator.
                participation.times_flagged += 1

        # Yield the data for each student, compiled into a string.
        for uid in students:
            yield str(students[uid])


        # Check and handled operations that would overwrite existing files by not doing them.
        if os.path.exists(exp_path):
            raise KeyError("The desired export file already exists.")  # TODO: More elegant collision handling.

    # Open the final participation logging file and write the data for each student to it.
    with open(exp_path, 'w') as export_file:
        # First add the header so we can tell when the columns mean.
        export_file.write(f"{DELIMITER.join(('<Times Called>', '<Times Flagged>', '<First Name>', '<Last Name>', '<UOID>', '<Phonetic Spelling>', '<Reveal Code>', '<Logged Dates>'))}\n")
        # Then rite the date for eahc student as a delimited line of values.
        export_file.writelines(compile_final_participation_logs())

    pass
