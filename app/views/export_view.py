"""Vue : les fichiers produits (CSV et Excel)."""
from pathlib import Path

import config
from app.models.depot import DepotProduits


def _nom_feuille(nom: str) -> str:
    for caractere in '[]:*?/\\':
        nom = nom.replace(caractere, "-")
    return nom[:31] or "Sans nom"      # limite Excel : 31 caractères


class ExportView:
    def exporter_csv(self, depot: DepotProduits) -> Path:
        config.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        # utf-8-sig : les accents s'affichent bien dans Excel ; ";" et "," : format français
        depot.vers_dataframe().to_csv(config.CSV_FILE, index=False, encoding="utf-8-sig",
                                      sep=";", decimal=",")
        return config.CSV_FILE

    def exporter_excel(self, depot: DepotProduits) -> Path:
        import pandas as pd

        config.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        df = depot.vers_dataframe()
        with pd.ExcelWriter(config.EXCEL_FILE, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Tous les produits", index=False)
            depot.resume_par_categorie().to_excel(writer, sheet_name="Résumé catégories", index=False)
            for categorie, sous_tableau in df.groupby("categorie", sort=False):
                sous_tableau.to_excel(writer, sheet_name=_nom_feuille(categorie), index=False)

            for feuille in writer.book.worksheets:
                feuille.freeze_panes = "A2"
                self._rendre_liens_cliquables(feuille, ("url_produit", "url_image"))
                for colonne in feuille.columns:
                    largeur = max(len(str(c.value)) if c.value is not None else 0 for c in colonne)
                    feuille.column_dimensions[colonne[0].column_letter].width = min(largeur + 2, 60)
        return config.EXCEL_FILE

    @staticmethod
    def _rendre_liens_cliquables(feuille, colonnes_liens) -> None:
        """Transforme les colonnes de liens en hyperliens : un clic ouvre la page dans le navigateur."""
        entetes = [cellule.value for cellule in feuille[1]]
        for nom_colonne in colonnes_liens:
            if nom_colonne not in entetes:
                continue
            numero = entetes.index(nom_colonne) + 1
            for ligne in range(2, feuille.max_row + 1):
                cellule = feuille.cell(row=ligne, column=numero)
                if cellule.value:
                    cellule.hyperlink = str(cellule.value)
                    cellule.style = "Hyperlink"
