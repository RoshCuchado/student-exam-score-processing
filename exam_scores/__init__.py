# -*- coding: utf-8 -*-
"""Student Examination Score Processing - core logic (no input()/print())."""

from exam_scores.scoring import (
    MIN_SCORE, MAX_SCORE, PASSING_AVERAGE,
    validate_student, parse_scores, add_student, process_student,
)
from exam_scores.sample_data import generate_students
from exam_scores.processing import (
    split_into_chunks, run_sequential, run_threading,
    run_multiprocessing, run_concurrent,
)
from exam_scores.performance import (
    time_run, compute_speedup, compute_efficiency,
    evaluate_performance, explain_results,
)
