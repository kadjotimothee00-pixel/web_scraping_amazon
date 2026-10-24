"""Vue : tout ce qui s'affiche à l'écran."""
import logging

import config


class ConsoleView:
    def __init__(self):
        self.log = logging.getLogger("amazon_scraper")
        if not self.log.handlers:
            self.log.setLevel(logging.INFO)
            fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
            handler = logging.StreamHandler()
            handler.setFormatter(fmt)
            self.log.addHandler(handler)

    def afficher_debut(self, nb_recherches: int) -> None:
        mode = "TEST" if config.TEST_MODE else "COMPLET"
        self.log.info("Démarrage (mode %s) : %d recherche(s) technologie", mode, nb_recherches)

    def afficher_recherche(self, nom: str) -> None:
        self.log.info("Recherche : %s", nom)

    def afficher_resultats(self, nb_produits: int) -> None:
        self.log.info("  %d articles récupérés", nb_produits)

    def afficher_aucun_resultat(self) -> None:
        self.log.warning("  Aucun article trouvé (sélecteurs ou blocage ?)")

    def afficher_avertissement(self, message: str) -> None:
        self.log.warning(message)

    def afficher_erreur(self, message: str) -> None:
        self.log.error(message)

    def afficher_arret_volontaire(self, raison, nb_produits: int) -> None:
        self.log.info("Arrêt volontaire : %s (ce n'est PAS un blocage). %d produits récupérés. "
                      "Augmente MAX_TOTAL_PAGES dans config.py pour aller plus loin.",
                      raison, nb_produits)

    def afficher_blocage(self, raison, nb_produits: int) -> None:
        self.log.error("ARRÊT : %s. Les %d produits déjà récupérés sont conservés. "
                       "Attends plusieurs heures avant de relancer, avec des volumes plus faibles.",
                       raison, nb_produits)

    def afficher_export(self, chemin) -> None:
        self.log.info("Fichier créé : %s", chemin)

    def afficher_resume(self, depot, doublons_retires: int) -> None:
        self.log.info("Terminé : %d produits (%d doublons retirés)", len(depot), doublons_retires)
        print()
        print(depot.resume_par_categorie().to_string(index=False))
        print()

    def afficher_base(self, chemin, produits) -> None:
        """Affiche le contenu de la base SQLite (lu depuis la base, pas depuis la mémoire)."""
        self.log.info("Base SQLite : %s (%d lignes)", chemin, len(produits))
        affichage = produits[["categorie", "marque", "nom", "prix_eur", "note", "nb_avis"]].copy()
        affichage["nom"] = affichage["nom"].str.slice(0, 45)     # lignes lisibles à l'écran
        affichage["nb_avis"] = affichage["nb_avis"].astype("Int64")
        print()
        print(affichage.to_string(index=False))
        print()
