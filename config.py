"""Configuration centrale du projet : scraping d'Amazon.fr, catégorie TECHNOLOGIE.

Tout ce qui change (recherches, limites, sélecteurs, chemins) est ici.
"""
from pathlib import Path

# --- Mode test : seulement 2 recherches pour vérifier que tout marche ---
TEST_MODE = True          # passe à False seulement quand le test est concluant

# --- Site cible : Amazon France ---
BASE_URL = "https://www.amazon.fr/"
SEARCH_URL = "https://www.amazon.fr/s"

# Rayons (départements) Amazon : limitent la recherche à une catégorie.
RAYON_HIGHTECH = "electronics"      # High-Tech
RAYON_INFORMATIQUE = "computers"    # Informatique

# "Catégories" = recherches par mots-clés dans les rayons technologiques.
# nom   : nom affiché dans les fichiers (une feuille Excel par nom)
# query : mots-clés cherchés sur Amazon
# rayon : rayon Amazon (vide "" = tout le site)
SEARCHES = [
    {"nom": "Téléviseurs", "query": "téléviseur", "rayon": RAYON_HIGHTECH},
    {"nom": "Enceintes Bluetooth", "query": "enceinte bluetooth", "rayon": RAYON_HIGHTECH},
    {"nom": "Smartphones", "query": "smartphone", "rayon": RAYON_HIGHTECH},
    {"nom": "Ordinateurs portables", "query": "ordinateur portable", "rayon": RAYON_INFORMATIQUE},
    {"nom": "Tablettes", "query": "tablette tactile", "rayon": RAYON_INFORMATIQUE},
    {"nom": "Écouteurs Bluetooth", "query": "écouteurs bluetooth", "rayon": RAYON_HIGHTECH},
    {"nom": "Casques audio", "query": "casque audio", "rayon": RAYON_HIGHTECH},
    {"nom": "Montres connectées", "query": "montre connectée", "rayon": RAYON_HIGHTECH},
    {"nom": "Claviers", "query": "clavier", "rayon": RAYON_INFORMATIQUE},
    {"nom": "Souris sans fil", "query": "souris sans fil", "rayon": RAYON_INFORMATIQUE},
    {"nom": "Batteries externes", "query": "batterie externe", "rayon": RAYON_HIGHTECH},
    {"nom": "Disques durs externes", "query": "disque dur externe", "rayon": RAYON_INFORMATIQUE},
    
]

# --- Sélecteurs CSS (structure des pages de résultats Amazon) ---
# À vérifier avec F12 si une colonne sort vide.
SELECTORS = {
    "item_card": 'div[data-component-type="s-search-result"]',
    "item_name": "h2",
    "item_price": "span.a-price:not(.a-text-price) span.a-offscreen",
    "item_old_price": "span.a-price.a-text-price span.a-offscreen",
    "item_rating": "span.a-icon-alt",
    "item_reviews": "span.s-underline-text",
    "item_image": "img.s-image",
    "item_sponsored": "span.puis-sponsored-label-text",
}

# --- Politesse envers le site : garde des valeurs basses ---
HEADLESS = False
PAGE_TIMEOUT = 15
DELAY_MIN = 5.0               # pause aléatoire entre deux pages (secondes)
DELAY_MAX = 10.0
# Une seule page de résultats par recherche : on garde les premiers articles affichés.
MAX_PRODUCTS_PER_SEARCH = 10
MAX_SEARCHES = 2 if TEST_MODE else None
# Plafond de sécurité : 1 page d'accueil + 1 page par recherche
MAX_TOTAL_PAGES = (MAX_SEARCHES or len(SEARCHES)) + 1


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"            # base SQLite (amazon_tech.db)
EXPORTS_DIR = ROOT_DIR / "exports"      # fichiers finaux CSV / Excel

CSV_FILE = EXPORTS_DIR / "amazon_tech.csv"
EXCEL_FILE = EXPORTS_DIR / "amazon_tech.xlsx"
SQLITE_FILE = DATA_DIR / "amazon_tech.db"        
