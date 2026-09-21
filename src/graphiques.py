from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from requetes import con, R1, R2, R3, R7

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)

BLEU, ORANGE = "#2a78d6", "#eb6834"
ENCRE, GRIS, MUET, GRILLE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"

plt.rcParams.update({
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    "axes.edgecolor": "#c3c2b7", "axes.labelcolor": GRIS, "text.color": ENCRE,
    "xtick.color": MUET, "ytick.color": MUET, "grid.color": GRILLE,
    "font.size": 11, "axes.titlesize": 14, "axes.titleweight": "bold",
})


def propre(ax, grille="y"):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis=grille, lw=0.8, zorder=0)
    ax.set_axisbelow(True)


# ---------- g1 : le predicteur ----------
d = pd.read_sql_query(R2, con)
x, w = np.arange(len(d)), 0.38
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.bar(x - w / 2, d["taux_oui"], w, color=BLEU, label="Réadmis un jour", zorder=2)
ax.bar(x + w / 2, d["taux_30j"], w, color=ORANGE, label="Réadmis sous 30 jours", zorder=2)
for xi, a, b in zip(x, d["taux_oui"], d["taux_30j"]):
    ax.text(xi - w / 2, a + 1.5, f"{a:.0f}", ha="center", fontsize=9, color=GRIS)
    ax.text(xi + w / 2, b + 1.5, f"{b:.0f}", ha="center", fontsize=9, color=GRIS)
ax.set_xticks(x, d["hosp_ant"])
ax.set_xlabel("Hospitalisations dans l'année précédente")
ax.set_ylabel("Taux de réadmission (%)")
ax.set_title("Le passé hospitalier prédit le retour")
ax.legend(frameon=False)
propre(ax)
fig.tight_layout()
fig.savefig(FIG / "g1_hospit_anterieures.png", dpi=150)
plt.close(fig)


# ----------g2 : destination de sortie ----------
d = pd.read_sql_query(R3, con).head(8).iloc[::-1]
noms = [n[:46] + "..." if len(n) > 46 else n for n in d["destination"]]
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(noms, d["taux_30j"], color=BLEU, height=0.62, zorder=2)
for i, v in enumerate(d["taux_30j"]):
    ax.text(v + 0.4, i, f"{v:.1f} %", va="center", fontsize=9.5, color=GRIS)
ax.set_xlabel("Réadmission sous 30 jours (%)")
ax.set_title("Où va le patient à sa sortie")
propre(ax, grille="x")
fig.tight_layout()
fig.savefig(FIG / "g2_destination.png", dpi=150)
plt.close(fig)


# ---------- g3 : la censure a droite ----------
d = pd.read_sql_query(R7, con)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6.4), sharex=True)
for ax, col, coul, titre in ((a1, "taux_oui", BLEU, "Réadmis un jour"),
                             (a2, "taux_30j", ORANGE, "Réadmis sous 30 jours")):
    ax.plot(d["periode"], d[col], color=coul, lw=2, marker="o", ms=7, zorder=2)
    ax.set_ylabel(titre + "\n(%)")
    propre(ax)
a2.set_xlabel("Tranche chronologique (10 % des séjours chacune)")
a1.set_title("La baisse est un artefact : censure à droite")
fig.tight_layout()
fig.savefig(FIG / "g3_derive.png", dpi=150)
plt.close(fig)



# ---------- g4 : familles de maladie ----------
d = pd.read_sql_query(R1, con).sort_values("taux_readmis")
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(d["famille"], d["taux_readmis"], color=BLEU, height=0.62, zorder=2)
for i, (v, n) in enumerate(zip(d["taux_readmis"], d["sejours"])):
    ax.text(v + 0.4, i, f"{v:.1f} %   ({n} séjours)", va="center", fontsize=9, color=GRIS)
ax.set_xlim(0, 56)
ax.set_xlabel("Réadmission, toutes durées (%)")
ax.set_title("Toutes les familles ne se ressemblent pas")
propre(ax, grille="x")
fig.tight_layout()
fig.savefig(FIG / "g4_familles.png", dpi=150)
plt.close(fig)

print("4 figures ecrites dans figures/")