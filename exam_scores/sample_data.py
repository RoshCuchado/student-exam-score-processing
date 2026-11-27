# -*- coding: utf-8 -*-
"""Sample student records for testing and for the performance comparison."""

import random

from exam_scores.scoring import MAX_SCORE


# Create `count` students with 3 random scores each (same seed = same data)
def generate_students(count, seed=2024, subjects=3):
    if count < 0:
        raise ValueError("count must not be negative.")

    generator = random.Random(seed)
    students = []
    for number in range(1, count + 1):
        scores = [generator.randint(60, MAX_SCORE) for _ in range(subjects)]
        students.append((f"Student {number:05d}",) + tuple(scores))
    return students
