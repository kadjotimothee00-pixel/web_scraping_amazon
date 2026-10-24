"""Affiche le contenu de la base SQLite sans relancer le scraping : python consulter_base.py"""
import config
from app.models.base_sqlite import BaseSQLite
from app.views.console_view import ConsoleView


def main() -> None:
    if not config.SQLITE_FILE.exists():
        print("Aucune base trouvée : lance d'abord  python main.py")
        return
    base = BaseSQLite(config.SQLITE_FILE)
    ConsoleView().afficher_base(config.SQLITE_FILE, base.lire_produits())


if __name__ == "__main__":
    main()
