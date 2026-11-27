# -*- coding: utf-8 -*-
"""Tests for execution time, speedup, efficiency (R3) and the CLI layer."""

import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

from exam_scores import (
    time_run, compute_speedup, compute_efficiency, evaluate_performance,
    explain_results, generate_students,
)
import main


class TestMeasurements(unittest.TestCase):

    def test_time_run_returns_result_and_time(self):
        result, elapsed = time_run(sum, [1, 2, 3])
        self.assertEqual(result, 6)
        self.assertGreaterEqual(elapsed, 0)

    def test_speedup(self):
        self.assertEqual(compute_speedup(8.0, 2.0), 4.0)
        self.assertEqual(compute_speedup(1.0, 2.0), 0.5)

    def test_speedup_zero_time(self):
        with self.assertRaises(ValueError):
            compute_speedup(1.0, 0)

    def test_efficiency(self):
        self.assertEqual(compute_efficiency(3.0, 4), 0.75)

    def test_efficiency_bad_workers(self):
        with self.assertRaises(ValueError):
            compute_efficiency(2.0, 0)


class TestEvaluate(unittest.TestCase):

    def test_report_structure(self):
        report = evaluate_performance(generate_students(40), 2, 200)
        names = [row["implementation"] for row in report["rows"]]
        self.assertEqual(
            names,
            ["Sequential", "Threading", "Multiprocessing", "ThreadPoolExecutor"],
        )
        self.assertTrue(report["results_match"])
        self.assertEqual(report["records"], 40)
        for row in report["rows"]:
            self.assertGreater(row["time"], 0)
            self.assertAlmostEqual(
                row["efficiency"], row["speedup"] / row["workers"]
            )
        self.assertEqual(report["rows"][0]["speedup"], 1.0)
        self.assertIsInstance(report["explanation"], str)

    def test_empty_students(self):
        with self.assertRaises(ValueError):
            evaluate_performance([], 4)

    def test_explanation_branches(self):
        report = {
            "records": 10, "workers": 4, "work": 0, "results_match": False,
            "rows": [
                {"implementation": "Sequential", "workers": 1, "time": 1.0,
                 "speedup": 1.0, "efficiency": 1.0},
                {"implementation": "Threading", "workers": 4, "time": 2.0,
                 "speedup": 0.5, "efficiency": 0.125},
                {"implementation": "Multiprocessing", "workers": 4,
                 "time": 0.5, "speedup": 2.0, "efficiency": 0.5},
            ],
        }
        text = explain_results(report)
        self.assertIn("Threading was not faster", text)
        self.assertIn("GIL", text)
        self.assertIn("Multiprocessing was faster", text)
        self.assertIn("Fastest implementation: Multiprocessing", text)
        self.assertIn("WARNING", text)


class TestDisplay(unittest.TestCase):

    def test_display_performance_prints_table(self):
        report = evaluate_performance(generate_students(10), 2, 100)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            main.display_performance(report)
        output = buffer.getvalue()
        for word in ("Time (s)", "Speedup", "Efficiency", "Explanation",
                     "Sequential", "Multiprocessing"):
            self.assertIn(word, output)

    def test_display_results_limits_rows(self):
        results = [{"name": f"S{i}", "scores": [80], "total": 80,
                    "average": 80, "status": "PASSED"} for i in range(15)]
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            main.display_results(results, limit=5)
        self.assertIn("and 10 more records", buffer.getvalue())

    def test_enter_student_valid_and_invalid(self):
        students = []
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            with mock.patch("builtins.input", side_effect=["Zed", "80 90"]):
                main.enter_student(students)
            with mock.patch("builtins.input", side_effect=["Yan", "80 150"]):
                main.enter_student(students)
            with mock.patch("builtins.input", side_effect=["Xia", "abc"]):
                main.enter_student(students)
        self.assertEqual(students, [("Zed", 80, 90)])
        self.assertEqual(buffer.getvalue().count("Invalid entry"), 2)


if __name__ == "__main__":
    unittest.main()
