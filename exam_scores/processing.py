# -*- coding: utf-8 -*-
"""Sequential and parallel processing of student records.

Every function takes the students list and returns a list of result
dictionaries in the SAME order as the input. Nothing is printed here.
"""

import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

from exam_scores.scoring import process_student


# Split the list into at most `parts` pieces, keeping the original order
def split_into_chunks(students, parts):
    if parts < 1:
        raise ValueError("parts must be at least 1.")
    if not students:
        return []

    size = -(-len(students) // parts)  # ceiling division
    return [students[i:i + size] for i in range(0, len(students), size)]


# Worker for one chunk (must be top-level so multiprocessing can pickle it)
def process_chunk(task):
    chunk, work = task
    return [process_student(student, work) for student in chunk]


def rank_class(results):
    """Competition ranks by displayed average, preserving input order."""
    ranks = {}
    for position, average in enumerate(sorted((r["average"] for r in results), reverse=True), 1):
        ranks.setdefault(average, position)
    for row in results:
        row["rank"] = ranks[row["average"]]
    return results


def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


# SEQUENTIAL: one student after another
def run_sequential(students, work=0):
    return rank_class([process_student(student, work) for student in students])


# PARALLEL 1: THREADING (one thread per chunk)
def run_threading(students, workers=4, work=0):
    chunks = split_into_chunks(students, workers)
    outputs = [None] * len(chunks)
    errors = []

    def worker(index, chunk):
        try:
            outputs[index] = process_chunk((chunk, work))
        except ValueError as error:  # invalid record: report it after join
            errors.append(error)

    threads = []
    for index, chunk in enumerate(chunks):
        thread = threading.Thread(target=worker, args=(index, chunk))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    if errors:
        raise errors[0]

    return rank_class(flatten(outputs))


# PARALLEL 2: MULTIPROCESSING (process pool)
def run_multiprocessing(students, workers=4, work=0):
    chunks = split_into_chunks(students, workers)
    if not chunks:
        return []

    tasks = [(chunk, work) for chunk in chunks]
    with multiprocessing.Pool(processes=workers) as pool:
        outputs = pool.map(process_chunk, tasks)

    return rank_class(flatten(outputs))


# PARALLEL 3: CONCURRENT (concurrent.futures.ThreadPoolExecutor)
def run_concurrent(students, workers=4, work=0):
    chunks = split_into_chunks(students, workers)
    if not chunks:
        return []

    tasks = [(chunk, work) for chunk in chunks]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        outputs = list(executor.map(process_chunk, tasks))

    return rank_class(flatten(outputs))
