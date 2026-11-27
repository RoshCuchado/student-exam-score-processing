# -*- coding: utf-8 -*-
"""Student Examination Score Processing - menu (CLI) layer.

All logic lives in the exam_scores package. This file only asks for input
and prints the results.
"""

import os
import textwrap
from exam_scores.scoring import StudentName
import csv
import sys
import json
import math
from pathlib import Path
from statistics import median

from exam_scores import (
    add_student, parse_scores, generate_students, evaluate_performance,
    run_sequential, run_threading, run_multiprocessing, run_concurrent,
    time_run,
)

WORKERS = 4          # number of threads / processes used by parallel runs
WORK_LOOPS = 0   # simulated processing cost per student record
SHOW_LIMIT = 10      # rows printed for a long list of results


# Print student results as a table (first `limit` rows only)
def result_headers(subjects):
    details = [f"{subject} {field}" for subject in subjects for field in ("Grade", "Status")]
    return ["Name", "First Name", "Last Name", *(f"{s} Score" for s in subjects),
            "Total", "Average", "Overall Status", "Overall Grade", "Class Rank", *details]


def display_results(results, limit=SHOW_LIMIT, subjects=None):
    from exam_scores.scoring import grade_and_status
    for row in results[:limit]:
        print(row["name"])
        print(f"{'Subject':<32}  {'Score':>8}  Grade  Status")
        print("-" * 59)
        details = row.get("subject_results")
        for index, score in enumerate(row["scores"]):
            subject = subjects[index] if subjects and index < len(subjects) else f"Subject {index + 1}"
            grade, status = details[index] if details else grade_and_status(score)
            lines = textwrap.wrap(subject, 32)
            print(f"{lines[0]:<32}  {str(score).removesuffix('.0'):>8}  {grade:<5}  {status}")
            for line in lines[1:]:
                print(line)
        print("-" * 59)
        print(f"Total: {row['total']:.2f}   Average: {row['average']:.2f}")
        print(f"Overall grade: {row.get('grade', '-')}   Status: {row['status']}   Class rank: {row.get('rank', '-')}")
    if len(results) > limit:
        print(f"... and {len(results) - limit} more records")


# Print the performance table, speedup, efficiency, and explanation
def display_performance(report):
    print(f"\nRecords: {report['records']} | Workers: {report['workers']} "
          f"| Simulated work per record: {report['work']} loops")
    header = (f"{'Implementation':<20} | {'Workers':>7} | "
              f"{'Time (s)':>10} | {'Speedup':>8} | {'Efficiency':>10}")
    print(header)
    print("-" * len(header))
    for row in report["rows"]:
        print(f"{row['implementation']:<20} | {row['workers']:>7} | "
              f"{row['time']:>10.4f} | {row['speedup']:>7.2f}x | "
              f"{row['efficiency'] * 100:>9.1f}%")
    match = "YES" if report["results_match"] else "NO"
    print(f"\nParallel results identical to sequential: {match}")
    print("\nExplanation:")
    print(report["explanation"])


# SCORE ENTRY: ask for a name and scores, then store the record
def enter_student(students, subjects=None):
    print("\n--- ENTER STUDENT SCORES ---")
    if subjects:
        name = StudentName(input("First name: ").strip(), input("Last name: ").strip())
        if not all(name):
            print("Enter both first and last name.")
            return
        scores = []
        for subject in subjects:
            while True:
                try:
                    score = float(input(f"{subject} exam score (0-100): "))
                    if math.isfinite(score) and 0 <= score <= 100:
                        scores.append(score)
                        break
                except ValueError:
                    pass
                print("Enter a number from 0 to 100.")
        try:
            add_student(students, name, scores)
            print(f"Record added for {name.first} {name.last}.")
        except ValueError as error:
            print(f"Invalid entry: {error}")
        return
    name = input("Student name: ")
    scores_text = input("Scores (separated by spaces, 0-100): ")
    try:
        scores = parse_scores(scores_text)
        add_student(students, name, scores)
        print(f"Record added for {name.strip()}.")
    except ValueError as error:
        print(f"Invalid entry: {error}")


# Run one implementation and show its output and execution time
def read_viewer_action(prompt):
    if sys.platform != "win32" or not sys.stdin.isatty():
        return input(prompt).strip().lower() or "open"
    import msvcrt
    print(prompt, end="", flush=True)
    key = msvcrt.getwch()
    if key in ("\x00", "\xe0"):
        return {"H": "up", "P": "down", "K": "left", "M": "right"}.get(msvcrt.getwch(), "")
    if key == "\x03":
        raise KeyboardInterrupt
    return "open" if key == "\r" else key.lower()


def find_student(results):
    last = input("Last name (Enter to cancel): ").strip().casefold()
    if not last:
        return None
    first = input("First name (optional): ").strip().casefold()
    matches = [i for i, row in enumerate(results) if row["last_name"].casefold() == last
               and (not first or row["first_name"].casefold() == first)]
    if not matches:
        print("No matching students.")
        return None
    if len(matches) == 1:
        return matches[0]
    for number, i in enumerate(matches, 1):
        print(f"{number}. {results[i]['name']}")
    while True:
        choice = input("Choose a name by number (Enter to cancel): ").strip()
        if not choice:
            return None
        if choice in {str(n) for n in range(1, len(matches) + 1)}:
            return matches[int(choice) - 1]


def show_class(results, subjects, index):
    start = index // SHOW_LIMIT * SHOW_LIMIT
    rows = []
    for row in results[start:start + SHOW_LIMIT]:
        rows.append([row["name"], *(str(x).removesuffix(".0") for x in row["scores"]),
                     f"{row['total']:.2f}", f"{row['average']:.2f}", row["status"], row["grade"], str(row["rank"])])
    headers = ["Name", *subjects, "Total", "Average", "Status", "Grade", "Rank"]
    widths = [max(map(len, col)) for col in zip(headers, *rows)]
    def line(cells):
        return " | ".join(value.ljust(width) for value, width in zip(cells, widths))
    print("  " + line(headers))
    print("-" * (len(line(headers)) + 2))
    for i, row in enumerate(rows, start):
        print(("> " if i == index else "  ") + line(row))


def run_one(label, func, students, workers=WORKERS, subjects=None):
    print(f"\n--- {label.upper()} ---")
    if not students:
        print("No student records to process.")
        return
    results, elapsed = time_run(func, students, workers, WORK_LOOPS)
    print(f"\nExecution time: {elapsed:.4f} seconds")

    index = 0
    detail = False
    while True:
        if sys.platform == "win32" and sys.stdout.isatty():
            os.system("cls")
        print(f"{label} | {elapsed:.4f} seconds | Student {index + 1} of {len(results)}")
        if detail:
            display_results([results[index]], subjects=subjects)
            prompt = "[Left/Right] Student | [B] Class table"
        else:
            show_class(results, subjects, index)
            prompt = "[Up/Down] Select row | [Enter] Student details"
        action = read_viewer_action(f"{prompt} | [S] Search | [Q] Menu: ")
        if action == "q":
            return
        if action == "s":
            match = find_student(results)
            if match is not None:
                index, detail = match, True
            else:
                input("Press Enter to return.")
        elif action == "open":
            detail = True
        elif action == "b":
            detail = False
        elif action == ("right" if detail else "down"):
            index = min(index + 1, len(results) - 1)
        elif action == ("left" if detail else "up"):
            index = max(index - 1, 0)


# Ask for a number, using a default when the user presses Enter
def ask_number(prompt, default):
    text = input(f"{prompt} [{default}]: ").strip()
    if text == "":
        return default
    try:
        value = int(text)
    except ValueError:
        print("Not a whole number. Using the default.")
        return default
    if value < 1:
        print("Must be at least 1. Using the default.")
        return default
    return value


SUBJECT_FILE = Path(__file__).with_name("subjects.json")


def validate_subjects(names):
    if not isinstance(names, list) or not names or any(not isinstance(n, str) or not n.strip() for n in names):
        raise ValueError("Enter at least one subject and give each subject a name.")
    names = [n.strip() for n in names]
    if len({n.casefold() for n in names}) != len(names):
        raise ValueError("Each subject needs a unique name.")
    return names


def benchmark(subject_count):
    print("Median of three runs, including worker startup and class ranking.")
    for count in (100, 2000, 10000):
        records = generate_students(count, subjects=subject_count)
        baseline, _ = time_run(run_sequential, records)
        serial = median(time_run(run_sequential, records)[1] for _ in range(3))
        for workers in (2, 4):
            times = []
            for _ in range(3):
                rows, elapsed = time_run(run_multiprocessing, records, workers)
                if rows != baseline:
                    raise ValueError("Benchmark outputs differ.")
                times.append(elapsed)
            parallel = median(times)
            speedup = serial / parallel
            print(f"{count} records | {workers} workers | sequential {serial:.5f}s | "
                  f"parallel {parallel:.5f}s | {speedup:.2f}x | efficiency {speedup/workers:.1%} | "
                  f"{'time saved' if parallel < serial else 'no time saved'}")


def prompt_subjects():
    print("Enter one subject per line. Press Enter on a blank line to finish.")
    names = []
    while True:
        name = input(f"Enter subject {len(names) + 1}: ").strip()
        if not name:
            return names
        if name.casefold() in {item.casefold() for item in names}:
            print("That subject is already on the list.")
        else:
            names.append(name)


def menu_panel(title, details, sections):
    width = 60
    border = "+" + "-" * (width + 2) + "+"

    def row(text):
        for line in textwrap.wrap(text, width) or [""]:
            print(f"| {line:<{width}} |")

    print()
    print(border)
    row(title)
    for detail in details:
        row(detail)
    for heading, items in sections:
        print(f"+-- {heading} " + "-" * (width - len(heading) - 2) + "+")
        for key, label in items:
            row(f"[{key}]  {label}")
    print(border)


def choose_csv_file(save=False):
    if save:
        print("Press Enter to choose a folder and filename in Save As.")
        print("Or type a new filename such as class_results.csv, or paste a full destination path.")
    else:
        print("Press Enter to browse for a CSV file, or paste its path below.")
        print("Windows tip: in File Explorer, right-click the CSV and choose Copy as path.")
    entry = input("CSV path [Enter = browse, 0 = back]: ").strip()
    if entry == "0":
        return ""
    if entry:
        return entry.strip('"')
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        print("File browsing is unavailable on this Python installation.")
    else:
        try:
            root = tk.Tk()
            try:
                root.withdraw()
                if save:
                    return filedialog.asksaveasfilename(
                        parent=root, title="Save class results as a new CSV",
                        initialfile="class_results.csv", defaultextension=".csv",
                        filetypes=[("CSV files", "*.csv")],
                    )
                return filedialog.askopenfilename(
                    parent=root, title="Select a class CSV file",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                )
            finally:
                root.destroy()
        except tk.TclError:
            print("The file picker could not open.")
    return input("Paste the CSV path, or press Enter to go back: ").strip().strip('"')


def read_class_csv(path):
    students = []
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        header = next(reader, [])
        columns = [label.strip().casefold() for label in header]
        if columns[:2] == ["first name", "last name"]:
            offset = 2
        elif columns[:1] in (["name"], ["student name"]):
            offset = 1
        else:
            raise ValueError("Start with First Name and Last Name, followed by subject columns.")
        subjects = validate_subjects(header[offset:])
        for row in reader:
            if not row:
                continue
            if len(row) != len(header):
                raise ValueError(f"Line {reader.line_num}: expected {len(header)} columns.")
            try:
                name = StudentName(row[0].strip(), row[1].strip()) if offset == 2 else row[0]
                add_student(students, name, [float(value) for value in row[offset:]])
            except ValueError as error:
                raise ValueError(f"Line {reader.line_num}: {error}") from error
    if not students:
        raise ValueError("The CSV contains no student records.")
    return subjects, students


def export_results(path, subjects, students):
    results = run_sequential(students)
    with path.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(result_headers(subjects))
        for row in results:
            details = [value for pair in row["subject_results"] for value in pair]
            writer.writerow([row["name"], row["first_name"], row["last_name"], *row["scores"],
                             row["total"], row["average"], row["status"], row["grade"], row["rank"], *details])


def main():
    subjects = ["Subject 1", "Subject 2", "Subject 3"]
    try:
        subjects = validate_subjects(json.loads(SUBJECT_FILE.read_text(encoding="utf8")))
    except FileNotFoundError:
        pass
    except (OSError, ValueError) as error:
        print(f"Could not load saved subjects: {error}. Using numbered subjects.")
    students = []
    methods = {"1": ("Multiprocessing", run_multiprocessing), "2": ("Threading", run_threading),
               "3": ("Thread pool", run_concurrent)}
    while True:
        menu_panel("STUDENT EXAMINATION SCORE PROCESSING",
                   [f"Subjects: {', '.join(subjects)}", f"Students loaded: {len(students)}"], [
            ("Prepare class", [(1, "Set subjects"), (2, "Enter a student's scores"),
                               (3, "Generate sample students"), ("I", "Import class from CSV")]),
            ("View class results", [(4, "Process sequentially"), (5, "Choose a parallel method"),
                                    ("E", "Export class results to CSV")]),
            ("Measure performance", [(6, "Compare methods on this class"),
                                     (7, "Benchmark different class sizes and worker counts")]),
            ("Session", [(8, "Exit")]),
        ])
        choice = input("\nChoose an option [1-8, I or E]: ").strip().lower()
        if choice in {"4", "5", "6", "e"} and not students:
            print("Enter, generate, or import students first.")
            continue
        if choice == "e":
            name = choose_csv_file(save=True)
            if not name:
                continue
            path = Path(name)
            if path.suffix.lower() != ".csv":
                path = Path(str(path) + ".csv")
            try:
                export_results(path, subjects, students)
                print(f"Saved {len(students)} student results to {path.resolve()}")
            except FileExistsError:
                print("That file already exists. Choose a new filename.")
            except OSError as error:
                print(f"Could not export results: {error}")
        elif choice == "i":
            path = choose_csv_file()
            if not path:
                continue
            try:
                names, records = read_class_csv(path)
            except (OSError, ValueError, csv.Error) as error:
                print(f"Could not import CSV: {error}")
                continue
            if students and input("Replace the current class [y/N]? ").strip().lower() != "y":
                continue
            subjects, students = names, records
            print(f"Imported {len(records)} students. Choose 4 or 5 to process their scores.")
        elif choice == "2":
            enter_student(students, subjects)
        elif choice == "3":
            if students and input("Replace current records with sample students [y/N]? ").strip().lower() != "y":
                continue
            students = generate_students(ask_number("How many students", 2000), subjects=len(subjects))
        elif choice == "4":
            run_one("Sequential", lambda s, w, k: run_sequential(s, k), students, subjects=subjects)
        elif choice == "5":
            menu_panel("PARALLEL PROCESSING", [], [("Choose method",
                       [(1, "Multiprocessing (default)"), (2, "Threading"), (3, "Thread pool"),
                        (0, "Back to main menu")])])
            method = input("\nChoose a method [default 1]: ").strip() or "1"
            if method == "0":
                continue
            if method in methods:
                label, func = methods[method]
                run_one(label, func, students, ask_number("Workers", WORKERS), subjects)
            else:
                print("Unknown method.")
        elif choice == "1":
            try:
                names = prompt_subjects()
                if not names or names == subjects:
                    continue
                if students and names != subjects and input("Changing subjects clears the current roster. Continue [y/N]? ").lower() != "y":
                    continue
                temporary = SUBJECT_FILE.with_suffix(".tmp")
                temporary.write_text(json.dumps(names, ensure_ascii=False), encoding="utf8")
                temporary.replace(SUBJECT_FILE)
                if names != subjects:
                    students = []
                subjects = names
                print("Subjects saved.")
            except (OSError, ValueError) as error:
                print(f"Could not save subjects: {error}")
        elif choice == "7":
            benchmark(len(subjects))
        elif choice == "6":
            display_performance(evaluate_performance(students, ask_number("Workers", WORKERS), WORK_LOOPS))
        elif choice == "8":
            break
        else:
            print("Unknown option.")


if __name__ == "__main__":
    main()
