import sys, sqlite3, pandas as pd
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit('Usage : python src/sql.py "SELECT ..."')
con = sqlite3.connect(Path(__file__).resolve().parent.parent / "diabet" / "healthy.db")
print(pd.read_sql_query(sys.argv[1], con).to_string(index=False))

