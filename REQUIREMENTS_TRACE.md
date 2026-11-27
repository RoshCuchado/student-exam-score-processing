# Requirements Trace - Topic 2: Student Examination Score Processing

Source: `project_proposal.pdf` (Final Project Proposal and Development Guidelines,
Parallel and Distributed Computing - Laboratory).

Status values were filled in only after running the tests (50 passing) and the
program (outputs shown in README.md). `unittest` file names are in `tests/`.

## Topic selection (Section IV)

| Req ID | Verbatim requirement | Where implemented | Verified by | Status |
|---|---|---|---|---|
| T2 | "2. Student Examination Score Processing" | whole project; records = (name, scores...) in `exam_scores/scoring.py:82 process_student` | `test_scoring.py::TestProcessStudent` | PASS |

## Requirement 1 (Research and Scenario) - paper, not code

| Req ID | Verbatim requirement | Where implemented | Verified by | Status |
|---|---|---|---|---|
| R1 | "Project title / Background of the problem / Problem statement / Project objectives / Proposed solution using PDC concepts / Brief explanation of the parallel or distributed computing technique to be used" | Not part of the program. Belongs in the 3-5 page paper (Section V.1) | n/a | OUT OF SCOPE (not built) |

## Requirement 2 - Python Program Development

Verbatim: "2. Python Program Development. The application must include:
Working Python program. Sequential processing implementation. Parallel processing
implementation. Appropriate use of Python libraries such as threading,
multiprocessing, or concurrent. Display of program output. Execution time
measurement."

| Req ID | Verbatim requirement | Where implemented | Verified by | Status |
|---|---|---|---|---|
| R2.1 | "Working Python program." | `main.py` (menu), `exam_scores/` package | Full test run (50 OK); CLI run in README | PASS |
| R2.1a | (topic 2) score entry + validation: scores read for each student, bad input rejected | `scoring.py:63 add_student`, `scoring.py:18 validate_student`, `scoring.py:45 parse_scores`, `main.py:53 enter_student` | `TestValidation`, `TestScoreEntry`, `TestDisplay.test_enter_student_valid_and_invalid`; CLI run with 150 and "abc" rejected | PASS |
| R2.1b | (topic 2) examination score processing: total, average, PASSED/FAILED per student | `scoring.py:82 process_student` | `TestProcessStudent` (boundaries 75 / 74, rounding trap) | PASS |
| R2.2 | "Sequential processing implementation." | `processing.py:37 run_sequential` | `test_sequential_length_and_order`; baseline for all comparisons | PASS |
| R2.3 | "Parallel processing implementation." | `processing.py:42 run_threading`, `processing.py:69 run_multiprocessing`, `processing.py:82 run_concurrent` | `test_*_matches_sequential`, single worker, more workers than students, empty input, invalid record; speedup 1.68x measured for multiprocessing | PASS |
| R2.4 | "Appropriate use of Python libraries such as threading, multiprocessing, or concurrent." | `threading.Thread` (processing.py:42), `multiprocessing.Pool` (processing.py:69), `concurrent.futures.ThreadPoolExecutor` (processing.py:82) | all three named libraries used; results identical to sequential | PASS |
| R2.5 | "Display of program output." | `main.py:20 display_results`, `main.py:35 display_performance` | `TestDisplay`; CLI run in README | PASS |
| R2.6 | "Execution time measurement." | `performance.py:12 time_run` (`time.perf_counter`), used in `main.py:66 run_one` and `performance.py:34 evaluate_performance` | `test_time_run_returns_result_and_time`; "Execution time:" line in CLI run | PASS |

## Requirement 3 - Performance Evaluation

Verbatim: "3. Performance Evaluation. Students must compare sequential and parallel
processing using: Execution time. Speedup. Efficiency (if applicable). Brief
explanation of the results."

| Req ID | Verbatim requirement | Where implemented | Verified by | Status |
|---|---|---|---|---|
| R3.0 | "Students must compare sequential and parallel processing" | `performance.py:34 evaluate_performance` (runs Sequential + 3 parallel on same data; checks results equal) | `TestEvaluate.test_report_structure`; CLI option 7 | PASS |
| R3.1 | "Execution time" | `rows[i]["time"]` in `evaluate_performance`; printed by `main.py:35 display_performance` | `test_report_structure` (time > 0); README table | PASS |
| R3.2 | "Speedup" = sequential time / parallel time | `performance.py:20 compute_speedup` | `test_speedup`, `test_speedup_zero_time` | PASS |
| R3.3 | "Efficiency (if applicable)" = speedup / workers | `performance.py:27 compute_efficiency` | `test_efficiency`, `test_efficiency_bad_workers`, `test_report_structure` | PASS |
| R3.4 | "Brief explanation of the results." | `performance.py:80 explain_results` (text generated from measured numbers) | `test_explanation_branches`; "Explanation:" in README run | PASS |

## Other applicable items

| Req ID | Verbatim requirement | Where implemented | Verified by | Status |
|---|---|---|---|---|
| II.3 | "The application must include a comparison between sequential and parallel processing to evaluate performance." | same as R3.0 | CLI option 7 | PASS |
| G5 | "The application must demonstrate actual parallel or distributed processing." | `run_multiprocessing` runs chunks in separate processes (8-core machine) | Measured 1.68x speedup (1.55 s -> 0.92 s) in CLI run; threads show ~0.97x (GIL), reported honestly | PASS (multiprocessing); threading/ThreadPoolExecutor give no speedup on CPU-bound work |
| V.2 | "Complete and working Python program (.py files)." | `main.py`, `exam_scores/*.py` | tests + CLI run | PASS |
| V.1 | Short research paper (3-5 pages) | not part of the code | n/a | OUT OF SCOPE |
| V.3 | PowerPoint presentation with demonstration | not part of the code | n/a | OUT OF SCOPE |
| G1-G4, G6-G8 | Group size, leader, participation, approval, ability to explain code, presentation, deadline | people/process rules | n/a | NOT CODE |

## Assumptions (PDF is silent)

- A record is `(name, score1, score2, ...)`; each score must be a number from 0 to 100.
- "Processing" = total, average (2 decimals), PASSED if average >= 75 else FAILED (decided on the unrounded average).
- Per-record cost is simulated with a busy loop (`work` = 20000 loops) so parallelism is measurable. Results do not depend on it.
- Efficiency = speedup / number of workers (Sequential row = 1 worker = 100%).
