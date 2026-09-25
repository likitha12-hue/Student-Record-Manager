"""
Student Record Manager
----------------------
Features:
- Add Student
- Validate Email using Regex
- Save Data to a Text File in the same folder
- Read and display Student Data
- Handle Invalid Input using Custom Exceptions
"""

import os
import re
from typing import List, Optional


# ==========================================
# Custom Exception Classes
# ==========================================
class StudentRecordError(Exception):
    """Base exception class for Student Record Manager."""
    pass


class InvalidEmailError(StudentRecordError):
    """Raised when an email address does not match the valid format."""
    pass


class InvalidInputError(StudentRecordError):
    """Raised when user input fails validation constraints."""
    pass


class DuplicateRecordError(StudentRecordError):
    """Raised when attempting to add a student with an existing Roll Number."""
    pass


# ==========================================
# Student Class
# ==========================================
class Student:
    """Represents an individual student record."""

    def __init__(self, roll_no: str, name: str, email: str, course: str):
        self.roll_no = roll_no.strip()
        self.name = name.strip()
        self.email = email.strip()
        self.course = course.strip()

    def to_file_string(self) -> str:
        """Serialize student data for text file storage (delimited by pipe '|')."""
        return f"{self.roll_no}|{self.name}|{self.email}|{self.course}\n"

    @classmethod
    def from_file_string(cls, line: str) -> Optional["Student"]:
        """Parse a line from text file into a Student instance."""
        parts = line.strip().split("|")
        if len(parts) == 4:
            return cls(roll_no=parts[0], name=parts[1], email=parts[2], course=parts[3])
        return None

    def __str__(self) -> str:
        return f"Roll No: {self.roll_no:<8} | Name: {self.name:<18} | Email: {self.email:<28} | Course: {self.course}"


# ==========================================
# Validation Functions
# ==========================================
def validate_email(email: str) -> bool:
    """
    Validates email format using regular expressions.
    Accepts standard username@domain.extension format.
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.fullmatch(pattern, email.strip()):
        raise InvalidEmailError(f"'{email}' is not a valid email address. Example: student@domain.com")
    return True


def validate_name(name: str) -> str:
    """Validates student name (alphabets and spaces only, not empty)."""
    cleaned = name.strip()
    if not cleaned:
        raise InvalidInputError("Student name cannot be empty.")
    if not re.match(r"^[A-Za-z\s.'-]+$", cleaned):
        raise InvalidInputError("Student name can only contain letters, spaces, hyphens, and dots.")
    return cleaned


def validate_roll_no(roll_no: str) -> str:
    """Validates student roll number (alphanumeric, not empty)."""
    cleaned = roll_no.strip()
    if not cleaned:
        raise InvalidInputError("Roll number cannot be empty.")
    if not cleaned.isalnum():
        raise InvalidInputError("Roll number must be alphanumeric without spaces or special characters.")
    return cleaned


def validate_course(course: str) -> str:
    """Validates course name (not empty)."""
    cleaned = course.strip()
    if not cleaned:
        raise InvalidInputError("Course name cannot be empty.")
    return cleaned


# ==========================================
# File Storage Manager
# ==========================================
class StudentManager:
    """Handles business logic and file operations for student records."""

    def __init__(self, filename: str = "students.txt"):
        # Save the file in the exact same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(script_dir, filename)

    def load_all_students(self) -> List[Student]:
        """Reads and returns all student records from the text file."""
        students = []
        if not os.path.exists(self.file_path):
            return students

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    student = Student.from_file_string(line)
                    if student:
                        students.append(student)
                    else:
                        print(f"[Warning] Skipping corrupted line #{line_number} in file.")
        except IOError as e:
            print(f"[Error] Failed to read student records from file: {e}")

        return students

    def save_student(self, student: Student) -> None:
        """Appends a new student record to the text file."""
        try:
            with open(self.file_path, "a", encoding="utf-8") as file:
                file.write(student.to_file_string())
        except IOError as e:
            raise StudentRecordError(f"Failed to save student record to file: {e}")

    def is_roll_no_exists(self, roll_no: str) -> bool:
        """Checks if a roll number already exists in the file."""
        students = self.load_all_students()
        return any(s.roll_no.lower() == roll_no.lower() for s in students)


# ==========================================
# User Interface & Menu
# ==========================================
def add_student_flow(manager: StudentManager) -> None:
    """Guides user through adding a new student with validation & exception handling."""
    print("\n" + "=" * 45)
    print("           ADD NEW STUDENT")
    print("=" * 45)

    try:
        # 1. Roll Number
        raw_roll = input("Enter Roll Number (e.g. 101 or CS101): ")
        roll_no = validate_roll_no(raw_roll)

        if manager.is_roll_no_exists(roll_no):
            raise DuplicateRecordError(f"A student with Roll Number '{roll_no}' already exists!")

        # 2. Name
        raw_name = input("Enter Student Name: ")
        name = validate_name(raw_name)

        # 3. Email (Validated with Regex)
        raw_email = input("Enter Email Address: ")
        validate_email(raw_email)
        email = raw_email.strip()

        # 4. Course
        raw_course = input("Enter Course: ")
        course = validate_course(raw_course)

        # Create student and save to file
        new_student = Student(roll_no=roll_no, name=name, email=email, course=course)
        manager.save_student(new_student)

        print("-" * 45)
        print(" [SUCCESS] Student record saved successfully!")
        print(f" Saved to: {manager.file_path}")
        print("-" * 45)

    except InvalidEmailError as e:
        print(f"\n [Validation Error - Email]: {e}")
    except InvalidInputError as e:
        print(f"\n [Validation Error - Input]: {e}")
    except DuplicateRecordError as e:
        print(f"\n [Duplicate Error]: {e}")
    except StudentRecordError as e:
        print(f"\n [Record Error]: {e}")
    except Exception as e:
        print(f"\n [Unexpected Error]: {e}")


def display_students_flow(manager: StudentManager) -> None:
    """Reads and displays all student records in a formatted table."""
    print("\n" + "=" * 80)
    print("                          ALL STUDENT RECORDS")
    print("=" * 80)

    try:
        students = manager.load_all_students()

        if not students:
            print(" No student records found. File is empty or does not exist yet.")
            print(" Use Option 1 to add a student.")
            print("=" * 80)
            return

        header = f"{'Roll No':<10} | {'Name':<20} | {'Email':<30} | {'Course':<15}"
        print(header)
        print("-" * 80)
        for s in students:
            print(f"{s.roll_no:<10} | {s.name:<20} | {s.email:<30} | {s.course:<15}")

        print("=" * 80)
        print(f" Total Students: {len(students)}")
        print(f" Source: {manager.file_path}")
        print("=" * 80)

    except Exception as e:
        print(f" [Error reading records]: {e}")


def search_student_flow(manager: StudentManager) -> None:
    """Searches for a student by roll number."""
    print("\n" + "=" * 45)
    print("           SEARCH STUDENT RECORD")
    print("=" * 45)

    try:
        raw_roll = input("Enter Roll Number to search: ")
        roll_no = validate_roll_no(raw_roll)

        students = manager.load_all_students()
        match = next((s for s in students if s.roll_no.lower() == roll_no.lower()), None)

        if match:
            print("\n [Record Found]:")
            print(f"   Roll No : {match.roll_no}")
            print(f"   Name    : {match.name}")
            print(f"   Email   : {match.email}")
            print(f"   Course  : {match.course}")
        else:
            print(f"\n [Not Found] No student record matches Roll No '{roll_no}'.")
        print("=" * 45)

    except InvalidInputError as e:
        print(f"\n [Validation Error]: {e}")
    except Exception as e:
        print(f"\n [Error]: {e}")


def main():
    manager = StudentManager(filename="students.txt")

    while True:
        print("\n" + "=" * 40)
        print("    STUDENT RECORD MANAGEMENT SYSTEM")
        print("=" * 40)
        print(" 1. Add Student")
        print(" 2. View All Students")
        print(" 3. Search Student by Roll Number")
        print(" 4. Exit")
        print("=" * 40)

        try:
            choice = input("Enter your choice (1-4): ").strip()

            if not choice:
                raise InvalidInputError("Choice cannot be empty. Please enter 1, 2, 3, or 4.")

            if choice == "1":
                add_student_flow(manager)
            elif choice == "2":
                display_students_flow(manager)
            elif choice == "3":
                search_student_flow(manager)
            elif choice == "4":
                print("\n Thank you for using Student Record Manager. Goodbye!\n")
                break
            else:
                raise InvalidInputError(f"'{choice}' is an invalid choice. Please select 1, 2, 3, or 4.")

        except InvalidInputError as e:
            print(f"\n [Invalid Input]: {e}")
        except KeyboardInterrupt:
            print("\n\n Program interrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"\n [Unexpected Error]: {e}")


if __name__ == "__main__":
    main()
