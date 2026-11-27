# Student Examination Score Processing

Run `python main.py` or run the tests with `python -m unittest discover -s tests -t .`.

Use **Set subjects** to enter one subject name per prompt in score order and press Enter on a blank line to finish. The program stores them in subjects.json beside main.py. Manual entry prompts for each subject. Student records last for the current session.

Run Sequential processes the class in one process. Run Parallel offers multiprocessing, manual threading, and a thread pool. Compare all methods reports time, speedup, efficiency, and output equality for the current roster.

The benchmark compares 100, 2,000, and 10,000 generated records with two and four worker processes. It reports median timings from three runs, including startup and ranking, with simulated work disabled.

The project uses an example letter scale based on the unrounded average. A starts at 90, B at 85, C at 80, D at 75, and F is below 75. Passing starts at 75. Equal displayed averages share a class rank (1, 1, 3).
