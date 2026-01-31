@echo off
echo Construction de TS_Tool_Routier...
echo.

REM Vérifier que PyInstaller est installé
pip install pyinstaller --quiet

REM Construire l'exécutable
pyinstaller --name="TS_Tool_Routier" ^
            --windowed ^
            --icon=resources/icons/app_icon.ico ^
            --add-data="resources;resources" ^
            --add-data="README.md;." ^
            --clean ^
            --noconfirm ^
            src/main.py

echo.
echo ✅ Construction terminée !
echo 📁 L'exécutable est dans: dist\TS_Tool_Routier\
echo.
pause
