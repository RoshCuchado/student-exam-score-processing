# -*- coding: utf-8 -*-
"""Score entry, validation, and computation for one student record.

A student record is a tuple: (name, score1, score2, ...), the same way the
laboratory stores students. Results are returned as dictionaries so they
can be turned into JSON or HTML later.
"""

from typing import NamedTuple
import math


class StudentName(NamedTuple):
    first: str
    last: str

# Assumptions (the PDF does not give these values)
MIN_SCORE = 0
MAX_SCORE = 100
PASSING_AVERAGE = 75


# Check one student record. Returns a list of error messages (empty = valid)
def validate_student(student):
    errors = []

    if not isinstance(student, (tuple, list)) or len(student) < 2:
        return ["Record must contain a name and at least one score."]

    name = student[0]
    scores = student[1:]

    if isinstance(name, StudentName):
        if not name.first.strip() or not name.last.strip():
            errors.append("Enter both first and last name.")
    elif not isinstance(name, str) or name.strip() == "":
        errors.append("Name must not be empty.")

    for score in scores:
        # bool is a subclass of int, so it is rejected first
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            errors.append(f"Score {score!r} is not a number.")
        elif math.isnan(score) or math.isinf(score):
            errors.append(f"Score {score!r} is not a valid number.")
        elif score < MIN_SCORE or score > MAX_SCORE:
            errors.append(
                f"Score {score} is out of range ({MIN_SCORE}-{MAX_SCORE})."
            )

    return errors


# Convert text such as "85 90, 88" into a list of numbers
def parse_scores(text):
    parts = text.replace(",", " ").split()
    if not parts:
        raise ValueError("Enter at least one score.")

    scores = []
    for part in parts:
        try:
            value = float(part)
        except ValueError:
            raise ValueError(f"'{part}' is not a number.")
        if math.isfinite(value) and value == int(value):
            value = int(value)
        scores.append(value)
    return scores


# SCORE ENTRY: validate, then add the record to the students list
def add_student(students, name, scores):
    clean_name = name.strip() if isinstance(name, str) else name
    student = (clean_name,) + tuple(scores)
    errors = validate_student(student)
    if errors:
        raise ValueError(" ".join(errors))
    students.append(student)
    return student


# Busy loop that stands in for the time a real record would take to process
def simulate_work(loops):
    total = 0
    for i in range(loops):
        total += i
    return total


def grade_and_status(score):
    for cutoff, grade in ((90, "A"), (85, "B"), (80, "C"), (PASSING_AVERAGE, "D")):
        if score >= cutoff:
            return grade, "PASSED"
    return "F", "FAILED"


# Process one student record: total, average, and PASSED/FAILED status
def process_student(student, work=0):
    errors = validate_student(student)
    if errors:
        raise ValueError(" ".join(errors))

    if work > 0:
        simulate_work(work)

    identity = student[0]
    if isinstance(identity, StudentName):
        first, last = identity
        name = f"{first} {last}"
    else:
        name = identity.strip()
        first, _, last = name.rpartition(" ")

    scores = list(student[1:])
    total = sum(scores)
    average = total / len(scores)
    grade, status = grade_and_status(average)

    return {
        "name": name,
        "first_name": first,
        "last_name": last,
        "scores": scores,
        "subject_results": [grade_and_status(score) for score in scores],
        "total": round(total, 2),
        "average": round(average, 2),
        "status": status,
        "grade": grade,
    }
