from pathlib import Path
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent

df = pd.read_csv(
    RACINE / "diabet" / "diabetic_data.csv",
    keep_default_na=False,
    na_values=["?"],
    low_memory=False,
)


# le patient reviendra-t-il un jour
df["readmis_oui"] = (df["readmitted"] != "NO").astype(int)

# reviendra-t-il sous 30 jours
df["readmis_30j"] = (df["readmitted"] == "<30").astype(int)

# quand reviendra - t - il (jamais / après 30j / sous 30j)
df["readmis_3cl"] = df["readmitted"].map({"NO": 0, ">30": 1, "<30": 2})

# combien de jours va-t-il rester
df["duree_sejour"] = df["time_in_hospital"]

manquants = df.isna().sum()
df = df.drop(columns=["weight", "payer_code"])

for col in ["race", "medical_specialty", "diag_1", "diag_2", "diag_3"]:
    df[col] = df[col].fillna("Inconnu")
#
# print("Trous restants :", df.isna().sum().sum())
# print("Dimensions     :", df.shape)

# print("Séjours  :", df["encounter_id"].nunique())
# print("Patients :", df["patient_nbr"].nunique())


visites = df["patient_nbr"].value_counts()
print("Record de séjours pour UN seul patient :", visites.max())

df = df.sort_values("encounter_id").drop_duplicates(subset="patient_nbr", keep="first")
print("Après déduplication :", df.shape)