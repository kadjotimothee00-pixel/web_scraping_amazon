"""Transformation du texte lu sur la page en valeurs exploitables.

- to_eur / to_rating / to_count : fonctions pures (faciles à tester)
- parser_carte : lit un bloc produit Selenium et construit un objet Produit
"""
import re

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import config
from app.models.produit import Produit

S = config.SELECTORS


# ---------- conversions de texte ----------
def to_eur(value):
    """'1 299,99 €' -> 1299.99 ; '12,99 €' -> 12.99 ; sinon None."""
    if not isinstance(value, str):
        return None
    m = re.search(r"\d[\d\s\u202f\u00a0.]*(?:,\d{1,2})?", value)
    if not m:
        return None
    s = re.sub(r"[\s\u202f\u00a0]", "", m.group())
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def to_rating(value):
    """'4,5 sur 5 étoiles' -> 4.5"""
    if not isinstance(value, str):
        return None
    m = re.search(r"\d+(?:[.,]\d+)?", value)
    return float(m.group().replace(",", ".")) if m else None


def to_count(value):
    """'1 234' -> 1234 ; '1,2 k' -> 1200"""
    if not isinstance(value, str):
        return None
    m = re.search(r"(\d[\d\s\u202f\u00a0.,]*)\s*([kK])?", value)
    if not m:
        return None
    num = re.sub(r"[\s\u202f\u00a0]", "", m.group(1))
    try:
        if m.group(2):
            return int(float(num.replace(",", ".")) * 1000)
        return int(re.sub(r"\D", "", num))
    except ValueError:
        return None


# ---------- lecture d'un élément Selenium ----------
def _texte(parent, css: str) -> str:
    try:
        el = parent.find_element(By.CSS_SELECTOR, css)
        return (el.get_attribute("textContent") or "").strip()
    except NoSuchElementException:
        return ""


def _attribut(parent, css: str, attr: str) -> str:
    try:
        return parent.find_element(By.CSS_SELECTOR, css).get_attribute(attr) or ""
    except NoSuchElementException:
        return ""


def parser_carte(carte, categorie: str) -> Produit | None:
    """Transforme un bloc produit (WebElement) en Produit. None si le bloc est inutilisable."""
    asin = carte.get_attribute("data-asin") or ""
    nom = _texte(carte, S["item_name"])
    if not asin or not nom:
        return None
    return Produit(
        categorie=categorie,
        asin=asin,
        nom=nom,
        prix_eur=to_eur(_texte(carte, S["item_price"])),
        prix_ancien_eur=to_eur(_texte(carte, S["item_old_price"])),
        note=to_rating(_texte(carte, S["item_rating"])),
        nb_avis=to_count(_texte(carte, S["item_reviews"])),
        sponsorise=bool(carte.find_elements(By.CSS_SELECTOR, S["item_sponsored"])),
        url_produit=f"https://www.amazon.fr/dp/{asin}",
        url_image=_attribut(carte, S["item_image"], "src"),
    )
