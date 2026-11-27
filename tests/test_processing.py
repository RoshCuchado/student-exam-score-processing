# -*- coding: utf-8 -*-
"""Tests for sequential and parallel processing (R2 implementations)."""

import unittest

from exam_scores import (
    split_into_chunks, run_sequential, run_threading,
    run_multiprocessing, run_concurrent, generate_students,
)


class TestChunks(unittest.TestCase):

    def test_order_and_content_kept(self):
        data = list(range(10))
        chunks = split_into_chunks(data, 3)
        self.assertEqual([x for c in chunks for x in c], data)

    def test_at_most_parts(self):
        self.assertLessEqual(len(split_into_chunks(list(range(10)), 3)), 3)

    def test_more_parts_than_items(self):
        chunks = split_into_chunks([1, 2], 8)
        self.assertEqual([x for c in chunks for x in c], [1, 2])

    def test_empty(self):
        self.assertEqual(split_into_chunks([], 4), [])

    def test_bad_parts(self):
        with self.assertRaises(ValueError):
            split_into_chunks([1], 0)


class TestImplementations(unittest.TestCase):

    def setUp(self):
        self.students = generate_students(37)
        self.expected = run_sequential(self.students)

    def test_sequential_length_and_order(self):
        self.assertEqual(len(self.expected), 37)
        names = [r["name"] for r in self.expected]
        self.assertEqual(names, [s[0] for s in self.students])

    def test_threading_matches_sequential(self):
        self.assertEqual(run_threading(self.students, 4), self.expected)

    def test_multiprocessing_matches_sequential(self):
        self.assertEqual(run_multiprocessing(self.students, 3), self.expected)

    def test_concurrent_matches_sequential(self):
        self.assertEqual(run_concurrent(self.students, 4), self.expected)

    def test_single_worker(self):
        self.assertEqual(run_threading(self.students, 1), self.expected)
        self.assertEqual(run_concurrent(self.students, 1), self.expected)

    def test_more_workers_than_students(self):
        few = self.students[:2]
        expected = run_sequential(few)
        self.assertEqual(run_threading(few, 8), expected)
        self.assertEqual(run_multiprocessing(few, 8), expected)
        self.assertEqual(run_concurrent(few, 8), expected)

    def test_empty_input(self):
        self.assertEqual(run_sequential([]), [])
        self.assertEqual(run_threading([], 4), [])
        self.assertEqual(run_multiprocessing([], 4), [])
        self.assertEqual(run_concurrent([], 4), [])

    def test_work_does_not_change_results(self):
        self.assertEqual(run_sequential(self.students, 100), self.expected)

    def test_invalid_record_raises(self):
        bad = self.students + [("Bad", 150, 90, 90)]
        with self.assertRaises(ValueError):
            run_sequential(bad)
        with self.assertRaises(ValueError):
            run_threading(bad, 2)
        with self.assertRaises(ValueError):
            run_multiprocessing(bad, 2)
        with self.assertRaises(ValueError):
            run_concurrent(bad, 2)


if __name__ == "__main__":
    unittest.main()
