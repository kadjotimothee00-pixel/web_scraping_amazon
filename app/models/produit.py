"""Modèle : un produit Amazon."""
from dataclasses import asdict, dataclass, field
from datetime import datetime

# Ordre des colonnes dans les fichiers CSV / Excel
COLONNES = [
    "categorie", "asin", "marque", "nom", "url_produit", "prix_eur", "prix_ancien_eur",
    "reduction_pct", "note", "nb_avis", "sponsorise", "url_image", "date_scraping",
]


def _maintenant() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Produit:
    categorie: str
    asin: str
    nom: str
    marque: str = ""
    prix_eur: float | None = None
    prix_ancien_eur: float | None = None
    note: float | None = None
    nb_avis: int | None = None
    sponsorise: bool = False
    url_produit: str = ""      # lien vers la page du produit sur amazon.fr
    url_image: str = ""        # lien vers la photo du produit
    date_scraping: str = field(default_factory=_maintenant)

    def __post_init__(self):
        # marque non fournie -> 1er mot du titre (approximation)
        if not self.marque and self.nom.strip():
            self.marque = self.nom.split()[0]

    @property
    def reduction_pct(self) -> int | None:
        """Pourcentage de réduction, calculé à partir des deux prix."""
        if self.prix_eur is None or not self.prix_ancien_eur:
            return None
        if self.prix_ancien_eur <= self.prix_eur:
            return None
        return round((self.prix_ancien_eur - self.prix_eur) / self.prix_ancien_eur * 100)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["reduction_pct"] = self.reduction_pct
        return {colonne: data[colonne] for colonne in COLONNES}
