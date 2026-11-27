# -*- coding: utf-8 -*-
"""Tests for score entry, validation, and computation (R2 data handling)."""

import unittest

from exam_scores import (
    validate_student, parse_scores, add_student, process_student,
    generate_students,
)


class TestValidation(unittest.TestCase):

    def test_valid_record(self):
        self.assertEqual(validate_student(("Ana", 85, 90, 88)), [])

    def test_boundary_scores_are_valid(self):
        self.assertEqual(validate_student(("Low", 0, 0, 0)), [])
        self.assertEqual(validate_student(("High", 100, 100, 100)), [])

    def test_score_above_range(self):
        self.assertTrue(validate_student(("A", 101, 90)))

    def test_score_below_range(self):
        self.assertTrue(validate_student(("A", -1, 90)))

    def test_non_numeric_score(self):
        self.assertTrue(validate_student(("A", "ninety", 90)))

    def test_bool_score_rejected(self):
        self.assertTrue(validate_student(("A", True, 90)))

    def test_nan_and_inf_rejected(self):
        self.assertTrue(validate_student(("A", float("nan"), 90)))
        self.assertTrue(validate_student(("A", float("inf"), 90)))

    def test_empty_name(self):
        self.assertTrue(validate_student(("   ", 80, 80)))

    def test_missing_scores(self):
        self.assertTrue(validate_student(("OnlyName",)))

    def test_empty_record(self):
        self.assertTrue(validate_student(()))
        self.assertTrue(validate_student(None))


class TestScoreEntry(unittest.TestCase):

    def test_parse_scores(self):
        self.assertEqual(parse_scores("85 90, 88.5"), [85, 90, 88.5])

    def test_parse_empty_text(self):
        with self.assertRaises(ValueError):
            parse_scores("   ")

    def test_parse_bad_text(self):
        with self.assertRaises(ValueError):
            parse_scores("85 abc")

    def test_add_student_stores_record(self):
        students = []
        add_student(students, "  Ben ", [78, 82])
        self.assertEqual(students, [("Ben", 78, 82)])

    def test_add_student_rejects_out_of_range(self):
        students = []
        with self.assertRaises(ValueError):
            add_student(students, "Ben", [78, 120])
        self.assertEqual(students, [])


class TestProcessStudent(unittest.TestCase):

    def test_total_and_average(self):
        result = process_student(("Ana", 85, 90, 88))
        self.assertEqual(result["name"], "Ana")
        self.assertEqual(result["total"], 263)
        self.assertEqual(result["average"], 87.67)
        self.assertEqual(result["status"], "PASSED")

    def test_pass_boundary(self):
        self.assertEqual(process_student(("A", 75, 75, 75))["status"], "PASSED")
        self.assertEqual(process_student(("A", 74, 75, 75))["status"], "FAILED")

    def test_failed(self):
        self.assertEqual(process_student(("A", 50, 60))["status"], "FAILED")

    def test_unrounded_average_decides_status(self):
        # average is 74.9967 -> rounds to 75.0 but must still FAIL
        result = process_student(("A", 74.99, 74.99, 75))
        self.assertEqual(result["status"], "FAILED")

    def test_invalid_record_raises(self):
        with self.assertRaises(ValueError):
            process_student(("A", 101, 90))

    def test_result_is_json_friendly(self):
        import json
        json.dumps(process_student(("Ana", 85, 90, 88)))


class TestSampleData(unittest.TestCase):

    def test_count_and_validity(self):
        students = generate_students(50)
        self.assertEqual(len(students), 50)
        for student in students:
            self.assertEqual(validate_student(student), [])

    def test_same_seed_same_data(self):
        self.assertEqual(generate_students(10), generate_students(10))

    def test_zero_students(self):
        self.assertEqual(generate_students(0), [])

    def test_negative_count(self):
        with self.assertRaises(ValueError):
            generate_students(-1)


if __name__ == "__main__":
    unittest.main()
