"""Modèle : la base SQLite qui conserve les produits d'un lancement à l'autre.

Utilise le module `sqlite3` fourni avec Python : rien de plus à installer.
Un produit est identifié par (categorie, asin) : si on relance le scraping,
la ligne existante est mise à jour (prix, note...) au lieu d'être dupliquée.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import pandas as pd

from app.models.depot import DepotProduits
from app.models.produit import COLONNES

_CREATION_TABLE = """
CREATE TABLE IF NOT EXISTS produits (
    categorie        TEXT NOT NULL,
    asin             TEXT NOT NULL,
    marque           TEXT,
    nom              TEXT NOT NULL,
    url_produit      TEXT,
    prix_eur         REAL,
    prix_ancien_eur  REAL,
    reduction_pct    INTEGER,
    note             REAL,
    nb_avis          INTEGER,
    sponsorise       INTEGER NOT NULL DEFAULT 0,   -- 0 = non, 1 = oui
    url_image        TEXT,
    date_scraping    TEXT,
    PRIMARY KEY (categorie, asin)
)
"""

# INSERT, ou UPDATE si (categorie, asin) existe déjà
_COLONNES_A_METTRE_A_JOUR = [c for c in COLONNES if c not in ("categorie", "asin")]
_UPSERT = (
    f"INSERT INTO produits ({', '.join(COLONNES)}) "
    f"VALUES ({', '.join(':' + c for c in COLONNES)}) "
    f"ON CONFLICT(categorie, asin) DO UPDATE SET "
    f"{', '.join(f'{c} = excluded.{c}' for c in _COLONNES_A_METTRE_A_JOUR)}"
)


class BaseSQLite:
    def __init__(self, chemin: Path):
        self.chemin = Path(chemin)
        self.chemin.parent.mkdir(parents=True, exist_ok=True)
        with self._connexion() as conn:
            conn.execute(_CREATION_TABLE)

    @contextmanager
    def _connexion(self):
        """Ouvre la base, valide (commit) à la fin, puis ferme toujours le fichier."""
        conn = sqlite3.connect(self.chemin)
        try:
            with conn:                  # commit si OK, rollback si erreur
                yield conn
        finally:
            conn.close()

    # ---------- écriture ----------
    def enregistrer(self, depot: DepotProduits) -> int:
        """Écrit tous les produits du dépôt. Renvoie le nombre de lignes traitées."""
        lignes = [p.to_dict() for p in depot]
        with self._connexion() as conn:
            conn.executemany(_UPSERT, lignes)
        return len(lignes)

    # ---------- lecture ----------
    def lire_produits(self) -> pd.DataFrame:
        with self._connexion() as conn:
            return pd.read_sql_query(
                f"SELECT {', '.join(COLONNES)} FROM produits ORDER BY categorie, rowid", conn)

    def resume_par_categorie(self) -> pd.DataFrame:
        with self._connexion() as conn:
            return pd.read_sql_query(
                """SELECT categorie,
                          COUNT(*)                        AS nombre_produits,
                          ROUND(AVG(prix_eur), 1)         AS prix_moyen_eur,
                          MIN(prix_eur)                   AS prix_min_eur,
                          MAX(prix_eur)                   AS prix_max_eur,
                          ROUND(AVG(note), 1)             AS note_moyenne,
                          ROUND(AVG(sponsorise) * 100, 1) AS part_sponsorisee_pct
                   FROM produits GROUP BY categorie ORDER BY MIN(rowid)""", conn)

    def compter(self) -> int:
        with self._connexion() as conn:
            return conn.execute("SELECT COUNT(*) FROM produits").fetchone()[0]
