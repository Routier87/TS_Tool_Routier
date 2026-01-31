#!/usr/bin/env python3
"""
Script de construction de l'exécutable TS_Tool_Routier
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import json

class ExeBuilder:
    """Classe pour construire l'exécutable"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_dir = self.project_root / "src"
        self.resources_dir = self.project_root / "resources"
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        
        # Configuration
        self.app_name = "TS_Tool_Routier"
        self.version = "1.0.0"
        self.author = "Votre Nom"
        
        # Options PyInstaller
        self.pyinstaller_opts = [
            "--name", self.app_name,
            "--windowed",  # Pas de console
            "--clean",     # Nettoyer le cache
            "--noconfirm", # Écraser sans demander
            "--onedir",    # Un dossier (plus facile à debug)
            # "--onefile",  # Un seul fichier (décommente pour onefile)
        ]
        
    def check_dependencies(self):
        """Vérifie que toutes les dépendances sont installées"""
        print("🔍 Vérification des dépendances...")
        
        required = ["PyQt6", "hexdump"]
        missing = []
        
        for package in required:
            try:
                __import__(package.replace("-", "_"))
                print(f"  ✅ {package}")
            except ImportError:
                missing.append(package)
                print(f"  ❌ {package}")
        
        if missing:
            print(f"\n❌ Dépendances manquantes: {', '.join(missing)}")
            print("Installez-les avec: pip install " + " ".join(missing))
            return False
        
        return True
    
    def prepare_resources(self):
        """Prépare les ressources pour l'inclusion"""
        print("📁 Préparation des ressources...")
        
        # Créer un dossier temporaire pour les ressources
        temp_resources = self.build_dir / "temp_resources"
        if temp_resources.exists():
            shutil.rmtree(temp_resources)
        
        # Copier toutes les ressources
        shutil.copytree(self.resources_dir, temp_resources)
        
        # Créer un fichier version.txt
        version_info = {
            "name": self.app_name,
            "version": self.version,
            "author": self.author,
            "build_date": subprocess.getoutput("date /t" if platform.system() == "Windows" else "date")
        }
        
        with open(temp_resources / "version.json", "w", encoding="utf-8") as f:
            json.dump(version_info, f, indent=2)
        
        print(f"  ✅ Ressources copiées: {temp_resources}")
        return temp_resources
    
    def build_with_pyinstaller(self, resources_dir):
        """Exécute PyInstaller"""
        print("🔨 Construction avec PyInstaller...")
        
        # Fichier spec personnalisé
        spec_file = self.project_root / f"{self.app_name}.spec"
        
        # Options supplémentaires
        opts = self.pyinstaller_opts.copy()
        
        # Ajouter l'icône si elle existe
        icon_path = self.resources_dir / "icons" / "app_icon.ico"
        if icon_path.exists():
            opts.extend(["--icon", str(icon_path)])
            print(f"  ✅ Icône utilisée: {icon_path}")
        else:
            print("  ⚠️  Icône non trouvée")
        
        # Ajouter les ressources
        opts.extend(["--add-data", f"{resources_dir}{os.pathsep}resources"])
        
        # Ajouter les données supplémentaires
        opts.extend(["--add-data", f"README.md{os.pathsep}."])
        
        # Fichier d'entrée
        entry_point = self.src_dir / "main.py"
        opts.append(str(entry_point))
        
        # Afficher la commande
        cmd = ["pyinstaller"] + opts
        print(f"  Commande: {' '.join(cmd)}")
        
        # Exécuter
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("  ✅ PyInstaller exécuté avec succès")
            
            # Afficher les avertissements
            if result.stderr:
                print("  ⚠️  Avertissements:")
                for line in result.stderr.split('\n'):
                    if line.strip():
                        print(f"    {line}")
                        
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Erreur PyInstaller: {e}")
            print(f"  Sortie: {e.stdout}")
            print(f"  Erreur: {e.stderr}")
            return False
        
        return True
    
    def create_installer(self):
        """Crée un installateur (Windows)"""
        if platform.system() != "Windows":
            print("⚠️  Création d'installateur seulement sur Windows")
            return False
        
        print("📦 Création de l'installateur...")
        
        # Script NSIS pour créer un installateur
        nsis_script = self.build_dir / "installer.nsi"
        
        nsis_content = f"""
; NSIS Installer Script for {self.app_name}
Unicode true
Name "{self.app_name}"
OutFile "{self.app_name}_Setup.exe"
InstallDir "$PROGRAMFILES\\{self.app_name}"
InstallDirRegKey HKLM "Software\\{self.app_name}" "Install_Dir"
RequestExecutionLevel admin

!include "MUI2.nsh"

; Interface
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${{BUILD_DIR}}\\LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "French"

; Sections
Section "{self.app_name} (requis)" SecMain
  SectionIn RO
  
  SetOutPath "$INSTDIR"
  
  ; Copier les fichiers
  File /r "${{DIST_DIR}}\\{self.app_name}\\*"
  
  ; Créer le menu Démarrer
  CreateDirectory "$SMPROGRAMS\\{self.app_name}"
  CreateShortcut "$SMPROGRAMS\\{self.app_name}\\{self.app_name}.lnk" "$INSTDIR\\{self.app_name}.exe"
  CreateShortcut "$SMPROGRAMS\\{self.app_name}\\Désinstaller.lnk" "$INSTDIR\\uninstall.exe"
  
  ; Créer la désinstallation
  WriteUninstaller "$INSTDIR\\uninstall.exe"
  
  ; Écrire les clés de registre
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.app_name}" \
                   "DisplayName" "{self.app_name}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.app_name}" \
                   "UninstallString" '"$INSTDIR\\uninstall.exe"'
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.app_name}" \
                   "DisplayVersion" "{self.version}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.app_name}" \
                   "Publisher" "{self.author}"
SectionEnd

Section "Raccourci Bureau" SecDesktop
  CreateShortcut "$DESKTOP\\{self.app_name}.lnk" "$INSTDIR\\{self.app_name}.exe"
SectionEnd

Section "Désinstallation" SecUninstall
  ; Supprimer les fichiers
  RMDir /r "$INSTDIR"
  
  ; Supprimer le menu Démarrer
  RMDir /r "$SMPROGRAMS\\{self.app_name}"
  
  ; Supprimer le raccourci bureau
  Delete "$DESKTOP\\{self.app_name}.lnk"
  
  ; Supprimer les clés de registre
  DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.app_name}"
  DeleteRegKey HKLM "Software\\{self.app_name}"
SectionEnd

; Descriptions
LangString DESC_SecMain ${{LANG_FRENCH}} "Composants principaux de {self.app_name}"
LangString DESC_SecDesktop ${{LANG_FRENCH}} "Crée un raccourci sur le Bureau"
LangString DESC_SecUninstall ${{LANG_FRENCH}} "Désinstalle {self.app_name}"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT $SecMain ${{DESC_SecMain}}
  !insertmacro MUI_DESCRIPTION_TEXT $SecDesktop ${{DESC_SecDesktop}}
  !insertmacro MUI_DESCRIPTION_TEXT $SecUninstall ${{DESC_SecUninstall}}
!insertmacro MUI_FUNCTION_DESCRIPTION_END
"""
        
        # Écrire le script NSIS
        with open(nsis_script, "w", encoding="utf-8") as f:
            f.write(nsis_content)
        
        print(f"  ✅ Script NSIS créé: {nsis_script}")
        print("  📝 Compilez-le avec NSIS pour créer l'installateur")
        
        return True
    
    def create_portable_package(self):
        """Crée un package portable (zip)"""
        print("🎒 Création du package portable...")
        
        # Chemin de l'exécutable
        if (self.dist_dir / self.app_name).exists():
            exe_dir = self.dist_dir / self.app_name
        else:
            # Mode onefile
            exe_path = list(self.dist_dir.glob(f"{self.app_name}.exe"))[0]
            exe_dir = exe_path.parent
        
        # Créer un dossier portable
        portable_dir = self.dist_dir / f"{self.app_name}_Portable"
        if portable_dir.exists():
            shutil.rmtree(portable_dir)
        
        # Copier l'exécutable et les ressources
        shutil.copytree(exe_dir, portable_dir)
        
        # Ajouter un README portable
        readme_content = f"""
# {self.app_name} - Version Portable

## 📦 Contenu
- {self.app_name}.exe : Application principale
- resources/ : Fichiers de configuration et icônes
- backups/ : Dossier pour les sauvegardes (créé automatiquement)
- logs/ : Dossier pour les logs (créé automatiquement)

## 🚀 Utilisation
1. Dézippez ce dossier où vous voulez
2. Lancez "{self.app_name}.exe"
3. Tous les fichiers sont stockés localement dans ce dossier

## ⚠️ Notes
- Version {self.version}
- Aucune installation nécessaire
- Ne modifie pas le registre Windows
- Peut être exécuté depuis une clé USB

## 📞 Support
En cas de problème, vérifiez les fichiers dans le dossier logs/
"""
        
        with open(portable_dir / "README_Portable.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        # Créer le ZIP
        import zipfile
        zip_path = self.dist_dir / f"{self.app_name}_v{self.version}_Portable.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(portable_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, portable_dir.parent)
                    zipf.write(file_path, arcname)
        
        print(f"  ✅ Package portable créé: {zip_path}")
        return True
    
    def cleanup(self):
        """Nettoyage"""
        print("🧹 Nettoyage...")
        
        # Supprimer le dossier build temporaire
        temp_resources = self.build_dir / "temp_resources"
        if temp_resources.exists():
            shutil.rmtree(temp_resources)
            print("  ✅ Dossiers temporaires nettoyés")
    
    def run(self):
        """Exécute tout le processus de build"""
        print(f"🚀 Construction de {self.app_name} v{self.version}")
        print("=" * 50)
        
        # 1. Vérifier les dépendances
        if not self.check_dependencies():
            return False
        
        # 2. Préparer les ressources
        resources_dir = self.prepare_resources()
        
        # 3. Construire avec PyInstaller
        if not self.build_with_pyinstaller(resources_dir):
            return False
        
        # 4. Créer le package portable
        self.create_portable_package()
        
        # 5. Créer l'installateur (Windows seulement)
        if platform.system() == "Windows":
            self.create_installer()
        
        # 6. Nettoyage
        self.cleanup()
        
        # 7. Afficher les résultats
        print("\n" + "=" * 50)
        print("✅ CONSTRUCTION TERMINÉE !")
        print("\n📁 Résultats dans le dossier 'dist/':")
        
        exe_path = self.dist_dir / self.app_name / f"{self.app_name}.exe"
        if exe_path.exists():
            print(f"  • Exécutable: {exe_path}")
            print(f"  • Taille: {exe_path.stat().st_size / (1024*1024):.2f} MB")
        
        portable_zip = self.dist_dir / f"{self.app_name}_v{self.version}_Portable.zip"
        if portable_zip.exists():
            print(f"  • Portable: {portable_zip}")
        
        print("\n🎮 Pour tester:")
        print(f"  Double-cliquez sur: dist/{self.app_name}/{self.app_name}.exe")
        
        return True

if __name__ == "__main__":
    builder = ExeBuilder()
    success = builder.run()
    
    if not success:
        print("\n❌ La construction a échoué")
        sys.exit(1)
