"""Point d'entrée : python main.py"""
from app.controllers.scraping_controller import ScrapingController
from app.views.console_view import ConsoleView
from app.views.export_view import ExportView


def main() -> None:
    ScrapingController(ConsoleView(), ExportView()).executer()


if __name__ == "__main__":
    main()
