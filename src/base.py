from pathlib import Path
import io
import pandas as pd
import sqlite3

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "diabet"

df = pd.read_csv(DOSSIER / "diabetic_propre.csv", keep_default_na=False, low_memory=False)
assert len(df) == 101766, f"Fichier propre incorrect : {len(df)} lignes"

texte = (DOSSIER / "IDS_mapping.csv").read_text().replace("\r\n", "\n")
b = texte.split("\n,\n")
dim_admission = pd.read_csv(io.StringIO(b[0]), keep_default_na=False)
dim_sortie    = pd.read_csv(io.StringIO(b[1]), keep_default_na=False)
dim_source    = pd.read_csv(io.StringIO(b[2]), keep_default_na=False)

for d in (dim_admission, dim_sortie, dim_source):
    d["description"] = d["description"].str.strip()

dim_patient = df.sort_values("encounter_id").drop_duplicates("patient_nbr")[["patient_nbr", "gender", "race"]]
dim_diagnostic = df[["diag_1", "famille"]].drop_duplicates("diag_1").rename(columns={"diag_1": "code"})

print("patients:", len(dim_patient), "| diagnostics:", len(dim_diagnostic))
print("admission:", len(dim_admission), "| sortie:", len(dim_sortie), "| source:", len(dim_source))
print(dim_sortie.head(3).to_string())




import sqlite3

MEDICAMENTS = [c for c in df.columns if set(df[c].unique()) <= {"No", "Steady", "Up", "Down"}]
assert len(MEDICAMENTS) == 21, MEDICAMENTS

fait_medicament = df.melt(id_vars="encounter_id", value_vars=MEDICAMENTS,
                          var_name="medicament", value_name="statut")
fait_medicament = fait_medicament[fait_medicament["statut"] != "No"]

COLONNES_FAIT = ["encounter_id", "patient_nbr", "admission_type_id", "discharge_disposition_id",
                 "admission_source_id", "diag_1", "diag_2", "diag_3", "age", "medical_specialty",
                 "time_in_hospital", "num_lab_procedures", "num_procedures", "num_medications",
                 "number_outpatient", "number_emergency", "number_inpatient", "number_diagnoses",
                 "max_glu_serum", "A1Cresult", "change", "diabetesMed",
                 "readmitted", "readmis_oui", "readmis_30j", "readmis_3cl",
                 "premier_sejour", "decede"]
fait_sejour = df[COLONNES_FAIT]

SCHEMA = """
PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS fait_medicament;
DROP TABLE IF EXISTS fait_sejour;
DROP TABLE IF EXISTS dim_patient;
DROP TABLE IF EXISTS dim_diagnostic;
DROP TABLE IF EXISTS dim_admission;
DROP TABLE IF EXISTS dim_sortie;
DROP TABLE IF EXISTS dim_source;

CREATE TABLE dim_patient    (patient_nbr INTEGER PRIMARY KEY, gender TEXT, race TEXT);
CREATE TABLE dim_diagnostic (code TEXT PRIMARY KEY, famille TEXT);
CREATE TABLE dim_admission  (admission_type_id INTEGER PRIMARY KEY, description TEXT);
CREATE TABLE dim_sortie     (discharge_disposition_id INTEGER PRIMARY KEY, description TEXT);
CREATE TABLE dim_source     (admission_source_id INTEGER PRIMARY KEY, description TEXT);

CREATE TABLE fait_sejour (
    encounter_id             INTEGER PRIMARY KEY,
    patient_nbr              INTEGER REFERENCES dim_patient(patient_nbr),
    admission_type_id        INTEGER REFERENCES dim_admission(admission_type_id),
    discharge_disposition_id INTEGER REFERENCES dim_sortie(discharge_disposition_id),
    admission_source_id      INTEGER REFERENCES dim_source(admission_source_id),
    diag_1 TEXT REFERENCES dim_diagnostic(code),
    diag_2 TEXT, diag_3 TEXT, age TEXT, medical_specialty TEXT,
    time_in_hospital INTEGER, num_lab_procedures INTEGER, num_procedures INTEGER,
    num_medications INTEGER, number_outpatient INTEGER, number_emergency INTEGER,
    number_inpatient INTEGER, number_diagnoses INTEGER,
    max_glu_serum TEXT, A1Cresult TEXT, change TEXT, diabetesMed TEXT,
    readmitted TEXT, readmis_oui INTEGER, readmis_30j INTEGER, readmis_3cl INTEGER,
    premier_sejour INTEGER, decede INTEGER
);

CREATE TABLE fait_medicament (
    encounter_id INTEGER REFERENCES fait_sejour(encounter_id),
    medicament TEXT,
    statut TEXT
);
"""

con = sqlite3.connect(DOSSIER / "healthy.db")
con.executescript(SCHEMA)

TABLES = [("dim_patient", dim_patient), ("dim_diagnostic", dim_diagnostic),
          ("dim_admission", dim_admission), ("dim_sortie", dim_sortie),
          ("dim_source", dim_source), ("fait_sejour", fait_sejour),
          ("fait_medicament", fait_medicament)]

for nom, table in TABLES:
    table.to_sql(nom, con, if_exists="append", index=False)
con.commit()

for nom, _ in TABLES:
    print(nom, con.execute(f"SELECT COUNT(*) FROM {nom}").fetchone()[0])