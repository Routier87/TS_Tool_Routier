#!/bin/bash
echo "Construction de TS_Tool_Routier..."
echo ""

# Vérifier que PyInstaller est installé
pip install pyinstaller --quiet

# Construire l'exécutable
pyinstaller --name="TS_Tool_Routier" \
            --windowed \
            --icon=resources/icons/app_icon.ico \
            --add-data="resources:resources" \
            --add-data="README.md:." \
            --clean \
            --noconfirm \
            src/main.py

echo ""
echo "✅ Construction terminée !"
echo "📁 L'exécutable est dans: dist/TS_Tool_Routier/"
echo ""
read -p "Appuyez sur Entrée pour continuer..."
