"""Modèle : le dépôt qui conserve tous les produits récupérés."""
import pandas as pd

from app.models.produit import COLONNES, Produit


class DepotProduits:
    def __init__(self):
        self._produits: list[Produit] = []

    # ---------- ajout / lecture ----------
    def ajouter(self, produit: Produit) -> None:
        self._produits.append(produit)

    def ajouter_plusieurs(self, produits: list[Produit]) -> None:
        self._produits.extend(produits)

    def __len__(self) -> int:
        return len(self._produits)

    def __iter__(self):
        return iter(self._produits)

    def categories(self) -> list[str]:
        return list(dict.fromkeys(p.categorie for p in self._produits))

    # ---------- traitement ----------
    def dedoublonner(self) -> int:
        """Un même produit (asin) ne reste qu'une fois par catégorie.
        La version non sponsorisée est préférée. Renvoie le nombre de lignes retirées."""
        meilleurs: dict[tuple[str, str], Produit] = {}
        for p in self._produits:
            cle = (p.asin, p.categorie)
            actuel = meilleurs.get(cle)
            if actuel is None or (actuel.sponsorise and not p.sponsorise):
                meilleurs[cle] = p
        retires = len(self._produits) - len(meilleurs)
        self._produits = list(meilleurs.values())
        return retires

    # ---------- sorties ----------
    def vers_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([p.to_dict() for p in self._produits], columns=COLONNES)

    def resume_par_categorie(self) -> pd.DataFrame:
        df = self.vers_dataframe()
        if df.empty:
            return pd.DataFrame(columns=["categorie", "nombre_produits"])
        return (
            df.groupby("categorie", sort=False)
            .agg(nombre_produits=("nom", "count"),
                 prix_moyen_eur=("prix_eur", "mean"),
                 prix_min_eur=("prix_eur", "min"),
                 prix_max_eur=("prix_eur", "max"),
                 note_moyenne=("note", "mean"),
                 part_sponsorisee_pct=("sponsorise", lambda s: s.mean() * 100))
            .round(1)
            .reset_index()
        )
