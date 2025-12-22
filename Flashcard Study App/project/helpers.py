
import os
from cs50 import SQL

# Connect to flashcards database using absolute path so it works from any CWD
BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "flashcards.db")
db = SQL(f"sqlite:///{DB_PATH}")
