"""Contrôleur : chef d'orchestre. Il relie le scraper, le modèle (dépôt) et les vues."""
import config
from app.models.base_sqlite import BaseSQLite
from app.models.depot import DepotProduits
from app.scraper.amazon_scraper import AmazonScraper, BlocageAmazon, PlafondAtteint
from app.scraper.driver import create_driver
from app.views.console_view import ConsoleView
from app.views.export_view import ExportView


class ScrapingController:
    def __init__(self, console: ConsoleView, export: ExportView):
        self.console = console
        self.export = export
        self.depot = DepotProduits()
        self.base = BaseSQLite(config.SQLITE_FILE)

    def executer(self) -> None:
        recherches = config.SEARCHES[: config.MAX_SEARCHES] if config.MAX_SEARCHES else config.SEARCHES
        self.console.afficher_debut(len(recherches))

        driver = create_driver()
        try:
            scraper = AmazonScraper(driver)
            scraper.ouvrir_accueil()
            for recherche in recherches:
                self._traiter_recherche(scraper, recherche)
                scraper.pause()
        except PlafondAtteint as exc:
            self.console.afficher_arret_volontaire(exc, len(self.depot))
        except BlocageAmazon as exc:
            self.console.afficher_blocage(exc, len(self.depot))
        except KeyboardInterrupt:
            self.console.afficher_avertissement("Interruption par l'utilisateur (Ctrl+C)")
        finally:
            driver.quit()

        self._finaliser()

    def _traiter_recherche(self, scraper: AmazonScraper, recherche: dict) -> None:
        self.console.afficher_recherche(recherche["nom"])
        try:
            produits = scraper.rechercher(recherche)
        except (PlafondAtteint, BlocageAmazon):
            raise   # gérés dans executer()
        except Exception as exc:  # une recherche qui plante ne doit pas tout arrêter
            self.console.afficher_erreur(f"Échec de la recherche « {recherche['nom']} » : {exc}")
            return
        if not produits:
            self.console.afficher_aucun_resultat()
            return
        self.depot.ajouter_plusieurs(produits)
        self.console.afficher_resultats(len(produits))

    def _finaliser(self) -> None:
        if len(self.depot) == 0:
            self.console.afficher_erreur("Aucune donnée récupérée : vérifie les sélecteurs dans config.py")
            return
        retires = self.depot.dedoublonner()
        self.console.afficher_export(self.export.exporter_csv(self.depot))
        self.console.afficher_export(self.export.exporter_excel(self.depot))
        self.console.afficher_resume(self.depot, retires)
        self.base.enregistrer(self.depot)                   # SQLite : mise à jour sans doublons
        self.console.afficher_base(config.SQLITE_FILE, self.base.lire_produits())
