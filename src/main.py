#!/usr/bin/env python3
"""
TS_Tool_Routier - Éditeur de sauvegardes Transport Fever 2
Auteur: [Ton Nom]
Version: 1.0.0
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    """Point d'entrée principal de l'application"""
    # Configuration des logs
    logger = setup_logger()
    logger.info("=== TS_Tool_Routier Démarrage ===")
    
    # Création de l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName("TS_Tool_Routier")
    app.setApplicationVersion("1.0.0")
    
    # Création de la fenêtre principale
    window = MainWindow()
    
    # Définir l'icône (à créer plus tard)
    # app_icon = QIcon("resources/icons/app_icon.png")
    # window.setWindowIcon(app_icon)
    
    window.show()
    
    # Exécution de l'application
    logger.info("Application lancée avec succès")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
