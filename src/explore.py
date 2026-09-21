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



visites = df["patient_nbr"].value_counts()



df = df.sort_values("encounter_id")
df["premier_sejour"] = (~df.duplicated(subset="patient_nbr")).astype(int)
df["decede"] = df["discharge_disposition_id"].isin([11, 13, 14, 19, 20, 21]).astype(int)

# --- 2.7 regrouper les 717 codes ICD-9 en 9 familles ---
def famille_maladie(code):
    if not code[:1].isdigit():
        return "Autre"
    n = float(code)
    if 250 <= n < 251:             return "Diabete"
    if 390 <= n < 460 or n == 785: return "Circulatoire"
    if 460 <= n < 520 or n == 786: return "Respiratoire"
    if 520 <= n < 580 or n == 787: return "Digestif"
    if 580 <= n < 630 or n == 788: return "Genito_urinaire"
    if 140 <= n < 240:             return "Tumeurs"
    if 710 <= n < 740:             return "Musculo_squelettique"
    if 800 <= n < 1000:            return "Traumatismes"
    return "Autre"

df["famille"] = df["diag_1"].apply(famille_maladie)

# --- 2.8 sauvegarder ---
df = df.drop(columns=["examide", "citoglipton"])
df.to_csv(RACINE / "diabet" / "diabetic_propre.csv", index=False)

assert len(df) == 101766, f"Attendu 101766 lignes, obtenu {len(df)}"
assert df["premier_sejour"].nunique() == 2, "Le flag premier_sejour n'a qu'une seule valeur"
print(df["famille"].value_counts().to_string())
print(df.groupby(["decede", "premier_sejour"]).size())
print("Fichier propre :", df.shape)