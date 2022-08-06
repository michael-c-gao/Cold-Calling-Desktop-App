from typing import Dict, Tuple, Iterable


class StudentDataManager:
    """ The software component responsible for holding the student roster.

    Attributes
    ----------
    StudentRoster (dict): The student roster.
    DeltaCreate (str): The value indicating that a new student has been added in GetRosterDiff.
    DeltaRemove (str): The value indicating that a student has been removed in GetRosterDiff.
    DeltaChange (str): The value indicating that a students data has been changed in GetRosterDiff.

    Methods
    -------
    GetStudentUid (str, str) -> str: Gets the unique identifier associated with a specific student.
    LoadRoster (Iterable[Iterable[str]]): Regenerates the student roster data from a new set of student entries.
    GetRosterDiff (dict): Gets the differences between a proposed student roster and the current student roster.
    """

    # The set of students indexed by their uid.
    StudentRoster = {}

    # Different type of changes
    DeltaCreate = "Created"
    DeltaRemove = "Removed"
    DeltaChange = "Changed"

    def GetStudentUid(fname: str, lname: str) -> str:
        ''' Generates a unique ID for a student from their name.

        Arguments
        ---------
        fname (str): The first name of the student.
        lname (str): The last name of the student.

        Returns
        -------
        str: A unique identifier based on the first and last name of a student.
        '''

        # Create and return a string based on the first and last name given as args.
        return f'fname={fname}&lname={lname}'

    def LoadRoster(students: Iterable[Iterable[str]]) -> None:
        ''' Overwrites the current student roster with data from a list of student entries.

        Arguments
        ---------
        students (Iterable[Iterable[str]]): A list of student entries to build the new roster from.
        '''

        # Remove all existant data from the student roster.
        StudentDataManager.StudentRoster.clear()

        # For each student in the given set...
        for student in students:
            # Get a new unique id for this student so they have something to be indexed by in the roster.
            uid = StudentDataManager.GetStudentUid(student[0], student[1])
            # Then add them to the roster.
            StudentDataManager.StudentRoster[uid] = student

    def GetRosterDiff(new_roster: Dict[str, Tuple[str, str, str, str, str]]):
        ''' Gets a list of changes to the current roster given another roster.
        '''

        # Get a reference to the StudentDataManager and the current student roster.
        SDM = StudentDataManager
        old_roster = SDM.StudentRoster

        # Prepare a list to hold all of the changes to the roster.
        roster_deltas = []

        # For each student in the incoming roster...
        for uid in new_roster:
            # Cache the proposed and current roster data for this student.
            new_data = new_roster[uid]
            old_data = old_roster.get(uid, None)

            # Prepare holders for how this student would to change and what about them would change.
            delta = None
            student_deltas = []

            # If we don't currently have any entry on this student they are being newly added.
            if old_data is None:
                # Register this fact.
                delta = SDM.DeltaCreate
                student_deltas.extend(new_data)
            else:
                # Otherwise, scan all of the entries in the student data for changes.
                for i in range(len(new_data)):
                    # Temporarily append even unchanged values to be logge if necessary.
                    student_deltas.append((new_data[i], old_data[i]))
                    # If the data has changed for this student, register that fact to be returned.
                    if new_data[i] != old_data[i]:
                        delta = SDM.DeltaChange

            # If we know that there is a change incoming we register to be returned.
            if delta is not None:
                roster_deltas.append((f'{new_data[0]} {new_data[1]}', delta, student_deltas))

        # For each of the current students...
        for uid in old_roster:
            # If they exist on the proposed roster we have already taken care of them. Don't bother here.
            if new_roster.get(uid, None) is not None:
                continue

            # Otherwise we know that they are being deleted and 
            old_data = old_roster[uid]
            roster_deltas.append((f'{old_data[0]} {old_data[1]}', SDM.DeltaRemove, []))

        # Return the set of changes that have been proposed to the roster.
        return roster_deltas
