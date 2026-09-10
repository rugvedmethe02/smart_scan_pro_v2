# Smart Scan Pro V2

Professional Tkinter SIH-style simulation prototype.

Pipeline: Synthetic PDWs -> HDBSCAN -> Activity Predictor -> Smart Scheduler -> Simulated HIT/MISS -> Feedback Learner.

Benchmark: Sequential vs Random vs Smart on the same synthetic environment.

Setup (Windows):
1. Install Python 3.10+.
2. Open CMD in this folder.
3. `python -m pip install -r requirements.txt`
4. `python generate_database.py`
5. `python benchmark.py`
6. `python main.py`

The UI is simulation-only. Ground truth is kept in the environment and is not supplied to the scheduler as future information. The synthetic emitter_id is used only for database ground truth/evaluation; HDBSCAN receives PDW features, not emitter IDs.

The displayed Pfa is explicitly labelled a prototype miss-rate proxy, not a calibrated receiver false-alarm probability.
