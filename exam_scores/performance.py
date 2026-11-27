# -*- coding: utf-8 -*-
"""Execution time, speedup, and efficiency for sequential vs. parallel runs."""

import time

from exam_scores.processing import (
    run_sequential, run_threading, run_multiprocessing, run_concurrent,
)


# Run func(*args) and return (result, execution time in seconds)
def time_run(func, *args):
    start = time.perf_counter()
    result = func(*args)
    elapsed = time.perf_counter() - start
    return result, elapsed


# Speedup = sequential time / parallel time
def compute_speedup(sequential_time, parallel_time):
    if parallel_time <= 0:
        raise ValueError("parallel_time must be greater than 0.")
    return sequential_time / parallel_time


# Efficiency = speedup / number of workers
def compute_efficiency(speedup, workers):
    if workers < 1:
        raise ValueError("workers must be at least 1.")
    return speedup / workers


# Run every implementation once and build the comparison table
def evaluate_performance(students, workers=4, work=0):
    if not students:
        raise ValueError("No student records to process.")

    baseline, sequential_time = time_run(run_sequential, students, work)

    rows = [{
        "implementation": "Sequential",
        "workers": 1,
        "time": sequential_time,
        "speedup": 1.0,
        "efficiency": 1.0,
    }]

    parallel_runs = [
        ("Threading", run_threading),
        ("Multiprocessing", run_multiprocessing),
        ("ThreadPoolExecutor", run_concurrent),
    ]

    results_match = True
    for label, func in parallel_runs:
        results, elapsed = time_run(func, students, workers, work)
        if results != baseline:
            results_match = False
        speedup = compute_speedup(sequential_time, elapsed)
        rows.append({
            "implementation": label,
            "workers": workers,
            "time": elapsed,
            "speedup": speedup,
            "efficiency": compute_efficiency(speedup, workers),
        })

    report = {
        "records": len(students),
        "workers": workers,
        "work": work,
        "rows": rows,
        "results_match": results_match,
    }
    report["explanation"] = explain_results(report)
    return report


# Short explanation built from the measured numbers
def explain_results(report):
    rows = report["rows"]
    sequential = rows[0]
    lines = [
        f"Sequential processing of {report['records']} records took "
        f"{sequential['time']:.4f} seconds."
    ]

    for row in rows[1:]:
        name = row["implementation"]
        if row["speedup"] > 1:
            lines.append(
                f"{name} was faster: speedup {row['speedup']:.2f}x, "
                f"efficiency {row['efficiency'] * 100:.1f}% "
                f"with {row['workers']} workers."
            )
        else:
            if "Thread" in name:
                reason = ("the GIL lets only one thread run Python code "
                          "at a time")
            else:
                reason = "starting the workers cost more than the work it saved"
            lines.append(
                f"{name} was not faster: speedup {row['speedup']:.2f}x "
                f"({reason})."
            )

    fastest = min(rows, key=lambda row: row["time"])
    lines.append(f"Fastest implementation: {fastest['implementation']}.")

    if not report["results_match"]:
        lines.append("WARNING: parallel results differ from sequential results.")
    return " ".join(lines)
