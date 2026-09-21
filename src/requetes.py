from pathlib import Path
import sqlite3
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
con = sqlite3.connect(RACINE / "diabet" / "healthy.db")

ETUDE = "f.decede = 0 AND f.premier_sejour = 1"

R1 = f"""
SELECT d.famille, COUNT(*) AS sejours,
       ROUND(AVG(f.readmis_oui) * 100, 1) AS taux_readmis,
       ROUND(AVG(f.readmis_30j) * 100, 1) AS taux_30j,
       ROUND(AVG(f.time_in_hospital), 1) AS duree_moy
FROM fait_sejour f JOIN dim_diagnostic d ON d.code = f.diag_1
WHERE {ETUDE}
GROUP BY d.famille ORDER BY taux_30j DESC
"""

R2 = f"""
SELECT f.number_inpatient AS hosp_ant, COUNT(*) AS sejours,
       ROUND(AVG(f.readmis_oui) * 100, 1) AS taux_oui,
       ROUND(AVG(f.readmis_30j) * 100, 1) AS taux_30j
FROM fait_sejour f WHERE {ETUDE}
GROUP BY f.number_inpatient HAVING sejours >= 30
ORDER BY hosp_ant
"""

R3 = f"""
SELECT s.description AS destination, COUNT(*) AS sejours,
       ROUND(AVG(f.readmis_oui) * 100, 1) AS taux_readmis,
       ROUND(AVG(f.readmis_30j) * 100, 1) AS taux_30j
FROM fait_sejour f JOIN dim_sortie s
  ON s.discharge_disposition_id = f.discharge_disposition_id
WHERE {ETUDE}
GROUP BY s.description HAVING sejours >= 300
ORDER BY taux_30j DESC
"""

R4 = f"""
SELECT m.medicament, m.statut, COUNT(*) AS sejours,
       ROUND(AVG(f.readmis_30j) * 100, 1) AS taux_30j
FROM fait_medicament m JOIN fait_sejour f ON f.encounter_id = m.encounter_id
WHERE {ETUDE} AND m.statut IN ('Up', 'Down', 'Steady')
GROUP BY m.medicament, m.statut HAVING sejours >= 300
ORDER BY taux_30j DESC LIMIT 15
"""

R5 = f"""
SELECT f.A1Cresult, f.change, COUNT(*) AS sejours,
       ROUND(AVG(f.readmis_oui) * 100, 1) AS taux_readmis
FROM fait_sejour f WHERE {ETUDE}
GROUP BY f.A1Cresult, f.change ORDER BY f.A1Cresult, f.change
"""

R6 = f"""
SELECT f.age, COUNT(*) AS sejours,
       ROUND(AVG(f.readmis_oui) * 100, 1) AS taux_readmis,
       ROUND(AVG(f.readmis_30j) * 100, 1) AS taux_30j
FROM fait_sejour f WHERE {ETUDE}
GROUP BY f.age ORDER BY f.age
"""

R7 = """
SELECT periode, COUNT(*) AS sejours,
       ROUND(AVG(readmis_oui) * 100, 1) AS taux_oui,
       ROUND(AVG(readmis_30j) * 100, 1) AS taux_30j
FROM (SELECT NTILE(10) OVER (ORDER BY encounter_id) AS periode, readmis_oui, readmis_30j
      FROM fait_sejour WHERE decede = 0 AND premier_sejour = 1)
GROUP BY periode ORDER BY periode
"""

REQUETES = {
    "R1 — Réadmission par famille de maladie": R1,
    "R2 — Effet des hospitalisations antérieures": R2,
    "R3 — Destination à la sortie": R3,
    "R4 — Traitements et réadmission à 30 jours": R4,
    "R5 — Le test HbA1c change-t-il quelque chose ?": R5,
    "R6 — Réadmission par tranche d'âge": R6,
    "R7 — Dérive dans le temps": R7,
}

if __name__ == "__main__":
    for titre, sql in REQUETES.items():
        print("\n" + titre)
        print(pd.read_sql_query(sql, con).to_string(index=False))