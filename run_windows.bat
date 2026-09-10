@echo off
python -m pip install -r requirements.txt
if not exist data\synthetic_pdws.csv python generate_database.py
python main.py
pause
