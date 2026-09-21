from pathlib import Path
import sqlite3
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
con = sqlite3.connect(RACINE / "diabet" / "healthy.db")

df = pd.read_sql_query(
    "SELECT * FROM fait_sejour WHERE decede = 0 AND premier_sejour = 1", con)

FUITES = ["encounter_id", "patient_nbr", "readmitted",
          "readmis_oui", "readmis_30j", "readmis_3cl",
          "decede", "premier_sejour"]

X = df.drop(columns=FUITES)
y = df["readmis_oui"]

print("X :", X.shape, "| y :", y.shape, "| taux de 1 :", round(y.mean(), 4))
print(X.dtypes.value_counts())