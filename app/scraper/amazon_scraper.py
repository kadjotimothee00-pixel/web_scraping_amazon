"""Navigation sur amazon.fr : charge UNE page de résultats par recherche et renvoie les premiers produits."""
import random
import time
from urllib.parse import urlencode

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config
from app.models.produit import Produit
from app.scraper.parsing import parser_carte

S = config.SELECTORS


class BlocageAmazon(Exception):
    """Amazon affiche un CAPTCHA : on s'arrête proprement (sans chercher à le contourner)."""


class PlafondAtteint(Exception):
    """Plafond MAX_TOTAL_PAGES atteint : arrêt volontaire, ce n'est pas un blocage."""


class AmazonScraper:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.PAGE_TIMEOUT)
        self.pages_chargees = 0

    # ---------- utilitaires ----------
    def pause(self) -> None:
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))

    def _fermer_bandeaux(self) -> None:
        """Accepte le bandeau cookies s'il est là (sans jamais planter)."""
        try:
            bouton = self.driver.find_element(By.ID, "sp-cc-accept")
            self.driver.execute_script("arguments[0].click();", bouton)
        except Exception:
            pass

    def _verifier_blocage(self) -> None:
        url = self.driver.current_url.lower()
        formulaires = self.driver.find_elements(By.CSS_SELECTOR, 'form[action*="validateCaptcha"]')
        if "captcha" in url or formulaires:
            raise BlocageAmazon("Amazon affiche un CAPTCHA")

    def _charger(self, url: str) -> None:
        """Seule méthode qui charge une page : compte les pages et vérifie le blocage."""
        if self.pages_chargees >= config.MAX_TOTAL_PAGES:
            raise PlafondAtteint(f"plafond de {config.MAX_TOTAL_PAGES} pages atteint")
        self.driver.get(url)
        self.pages_chargees += 1
        self._verifier_blocage()

    @staticmethod
    def _url_recherche(recherche: dict) -> str:
        params = {"k": recherche["query"]}
        if recherche.get("rayon"):
            params["i"] = recherche["rayon"]
        return f"{config.SEARCH_URL}?{urlencode(params)}"

    def _lire_page(self, categorie: str, limite: int) -> list[Produit]:
        """Lit les blocs produits dans l'ordre d'affichage et s'arrête dès qu'on en a `limite`."""
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, S["item_card"])))
        self._fermer_bandeaux()
        produits: list[Produit] = []
        for carte in self.driver.find_elements(By.CSS_SELECTOR, S["item_card"]):
            produit = parser_carte(carte, categorie)
            if produit is None:
                continue
            produits.append(produit)
            if len(produits) >= limite:
                break
        return produits

    # ---------- API utilisée par le contrôleur ----------
    def ouvrir_accueil(self) -> None:
        self._charger(config.BASE_URL)
        self._fermer_bandeaux()
        self.pause()

    def rechercher(self, recherche: dict) -> list[Produit]:
        """Charge la 1re page de résultats et renvoie ses premiers produits
        (MAX_PRODUCTS_PER_SEARCH). Renvoie une liste vide si aucun produit n'est trouvé."""
        self._charger(self._url_recherche(recherche))
        try:
            return self._lire_page(recherche["nom"], config.MAX_PRODUCTS_PER_SEARCH)
        except TimeoutException:
            return []
