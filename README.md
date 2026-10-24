# Amazon Scraper – catégorie Technologie

Programme Python (Selenium + pandas) qui visite **amazon.fr** et, pour chaque recherche
technologique (smartphones, ordinateurs portables, écouteurs, etc.), lit **une seule page de
résultats** et garde **les 10 premiers articles**. Il produit :

- `exports/amazon_tech.csv` : tous les articles (séparateur `;`, accents corrects dans Excel) ;
- `exports/amazon_tech.xlsx` : onglet « Tous les produits », onglet « Résumé catégories »
  et un onglet par catégorie ;
- `data/amazon_tech.db` : base **SQLite** (table `produits`, une ligne par produit et par
  catégorie ; relancer le programme met à jour les lignes existantes sans créer de doublons).

Colonnes : `categorie`, `asin`, `marque`, `nom`, `url_produit` (lien vers la page de l'article),
`prix_eur`, `prix_ancien_eur`, `reduction_pct`, `note`, `nb_avis`, `sponsorise`, `url_image`
(lien vers la photo), `date_scraping`. Dans l'Excel, les liens sont cliquables.

## Architecture (modèle MVC)

```
amazon_scraper/
├── main.py                       point d'entrée
├── consulter_base.py             affiche le contenu de la base sans relancer le scraping
├── config.py                     tous les réglages (recherches, limites, sélecteurs, chemins)
├── requirements.txt              bibliothèques à installer
├── app/
│   ├── controllers/
│   │   └── scraping_controller.py   chef d'orchestre : relie scraper, modèle et vues
│   ├── models/
│   │   ├── produit.py               un produit (dataclass) + calcul de la réduction
│   │   ├── depot.py                 dépôt de produits : doublons, DataFrame, résumé, JSON
│   │   └── base_sqlite.py           base SQLite : création de la table, enregistrement, lecture
│   ├── scraper/
│   │   ├── driver.py                crée le navigateur Chrome
│   │   ├── amazon_scraper.py        charge une page de résultats, détecte un blocage
│   │   └── parsing.py               texte de la page -> valeurs (prix, note, avis) -> Produit
│   └── views/
│       ├── console_view.py          affichages à l'écran et dans le journal
│       └── export_view.py           fichiers CSV et Excel
├── data/                         base SQLite (amazon_tech.db)
├── exports/                      fichiers finaux
└── tests/                        réservé aux tests
```

| Couche | Rôle |
|---|---|
| **Modèle** (`models/`) | Représente et stocke les données. Ne sait rien de Selenium ni de l'affichage. |
| **Vue** (`views/`) | Présente le résultat : écran, CSV, Excel. |
| **Contrôleur** (`controllers/`) | Décide de l'ordre des opérations et relie le reste. |
| **Scraper** (`scraper/`) | Seule partie qui dépend du site et de Selenium. |

## Installation

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Chrome doit être installé (Selenium télécharge tout seul le chromedriver).

## Utilisation

```
python main.py
```

Pour revoir les résultats stockés dans la base sans scraper : `python consulter_base.py`.

Lance toujours la commande **depuis le dossier qui contient `main.py`**.

### Régler le volume (dans `config.py`)

| Réglage | Rôle |
|---|---|
| `TEST_MODE` | `True` : 2 recherches seulement. `False` : toutes les recherches de `SEARCHES`. |
| `MAX_PRODUCTS_PER_SEARCH` | Nombre d'articles gardés par recherche (les premiers de la page). Réglé sur 10. |
| `MAX_SEARCHES` | Nombre de recherches traitées (`None` = toutes). |
| `MAX_TOTAL_PAGES` | Plafond de sécurité, calculé automatiquement : 1 page d'accueil + 1 page par recherche. |
| `DELAY_MIN`, `DELAY_MAX` | Pause aléatoire entre deux pages. Ne descends pas sous 5 secondes. |

Pour ajouter une catégorie technologique, ajoute une ligne dans `SEARCHES`.

## Précautions

- Les conditions d'utilisation d'Amazon interdisent l'extraction automatisée : garde de **petits
  volumes**, laisse **plusieurs heures** entre deux exécutions, et n'utilise pas les données hors
  d'un cadre d'étude.
- Si un CAPTCHA apparaît, le programme s'arrête et conserve les articles déjà récupérés. Il ne
  cherche pas à le contourner.
- Pour un usage réel, préfère l'API officielle **Product Advertising API** d'Amazon.
