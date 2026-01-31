"""
Gestionnaire de sauvegardes automatiques
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from .logger import get_logger

logger = get_logger(__name__)

class BackupManager:
    """Gère les sauvegardes automatiques des fichiers modifiés"""
    
    def __init__(self, backup_dir: str = "backups"):
        """
        Initialise le gestionnaire de sauvegardes
        
        Args:
            backup_dir: Répertoire pour les sauvegardes
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Structure: backups/YYYY-MM-DD/HH-MM-SS_originalname.save
        self.today_dir = self.backup_dir / datetime.now().strftime("%Y-%m-%d")
        self.today_dir.mkdir(exist_ok=True)
        
        logger.info(f"Gestionnaire de sauvegardes initialisé: {self.backup_dir}")
    
    def create_backup(self, filepath: str, suffix: str = "backup") -> Optional[str]:
        """
        Crée une sauvegarde d'un fichier
        
        Args:
            filepath: Chemin du fichier à sauvegarder
            suffix: Suffixe pour le nom de sauvegarde
            
        Returns:
            Chemin de la sauvegarde créée ou None
        """
        try:
            source_path = Path(filepath)
            if not source_path.exists():
                logger.error(f"Fichier source inexistant: {filepath}")
                return None
            
            # Générer un nom unique
            timestamp = datetime.now().strftime("%H-%M-%S")
            original_name = source_path.stem
            backup_name = f"{timestamp}_{original_name}_{suffix}{source_path.suffix}"
            
            backup_path = self.today_dir / backup_name
            
            # Copier le fichier
            shutil.copy2(source_path, backup_path)
            
            # Vérifier la copie
            if self.verify_backup(source_path, backup_path):
                logger.info(f"Sauvegarde créée: {backup_path}")
                return str(backup_path)
            else:
                logger.error("Échec vérification sauvegarde")
                if backup_path.exists():
                    backup_path.unlink()
                return None
                
        except Exception as e:
            logger.error(f"Erreur création sauvegarde: {e}")
            return None
    
    def verify_backup(self, original: Path, backup: Path) -> bool:
        """
        Vérifie qu'une sauvegarde est identique à l'original
        
        Args:
            original: Chemin du fichier original
            backup: Chemin de la sauvegarde
            
        Returns:
            True si identique, False sinon
        """
        try:
            if not original.exists() or not backup.exists():
                return False
            
            # Comparer les tailles
            if original.stat().st_size != backup.stat().st_size:
                return False
            
            # Comparer les contenus (hash)
            with open(original, 'rb') as f1, open(backup, 'rb') as f2:
                hash1 = hashlib.md5(f1.read()).hexdigest()
                hash2 = hashlib.md5(f2.read()).hexdigest()
                
                return hash1 == hash2
                
        except Exception as e:
            logger.error(f"Erreur vérification: {e}")
            return False
    
    def get_backups_for_file(self, original_path: str) -> List[str]:
        """
        Retourne la liste des sauvegardes pour un fichier
        
        Args:
            original_path: Chemin du fichier original
            
        Returns:
            Liste des chemins de sauvegarde
        """
        original_name = Path(original_path).stem
        backups = []
        
        # Chercher dans tous les sous-dossiers de backup
        for date_dir in self.backup_dir.iterdir():
            if date_dir.is_dir():
                for backup_file in date_dir.glob(f"*_{original_name}_*"):
                    if backup_file.is_file():
                        backups.append(str(backup_file))
        
        # Trier par date (le plus récent d'abord)
        backups.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
        
        return backups
    
    def cleanup_old_backups(self, days_to_keep: int = 7):
        """
        Supprime les sauvegardes trop anciennes
        
        Args:
            days_to_keep: Nombre de jours à conserver
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 86400)
            
            for date_dir in self.backup_dir.iterdir():
                if date_dir.is_dir():
                    # Vérifier si le dossier est trop vieux
                    dir_time = date_dir.stat().st_mtime
                    
                    if dir_time < cutoff_time:
                        # Supprimer tout le dossier
                        shutil.rmtree(date_dir)
                        logger.info(f"Dossier supprimé: {date_dir}")
                    else:
                        # Vérifier les fichiers individuels
                        for backup_file in date_dir.iterdir():
                            if backup_file.is_file():
                                file_time = backup_file.stat().st_mtime
                                if file_time < cutoff_time:
                                    backup_file.unlink()
                                    logger.info(f"Sauvegarde supprimée: {backup_file}")
                                    
        except Exception as e:
            logger.error(f"Erreur nettoyage sauvegardes: {e}")
    
    def restore_backup(self, backup_path: str, target_path: str) -> bool:
        """
        Restaure une sauvegarde
        
        Args:
            backup_path: Chemin de la sauvegarde
            target_path: Chemin de destination
            
        Returns:
            True si succès, False sinon
        """
        try:
            backup = Path(backup_path)
            target = Path(target_path)
            
            if not backup.exists():
                logger.error(f"Sauvegarde inexistante: {backup_path}")
                return False
            
            # Créer une sauvegarde de l'actuel avant restauration
            if target.exists():
                self.create_backup(str(target), "prerestore")
            
            # Restaurer
            shutil.copy2(backup, target)
            
            logger.info(f"Restauration: {backup_path} -> {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur restauration: {e}")
            return False
    
    def get_backup_stats(self) -> dict:
        """
        Retourne des statistiques sur les sauvegardes
        
        Returns:
            Dictionnaire de statistiques
        """
        stats = {
            'total_backups': 0,
            'total_size': 0,
            'by_date': {},
            'oldest': None,
            'newest': None
        }
        
        try:
            for date_dir in self.backup_dir.iterdir():
                if date_dir.is_dir():
                    date_stats = {
                        'count': 0,
                        'size': 0
                    }
                    
                    for backup_file in date_dir.iterdir():
                        if backup_file.is_file():
                            date_stats['count'] += 1
                            date_stats['size'] += backup_file.stat().st_size
                            
                            # Mettre à jour les plus anciens/récents
                            file_time = backup_file.stat().st_mtime
                            if (stats['oldest'] is None or 
                                file_time < stats['oldest'][0]):
                                stats['oldest'] = (file_time, str(backup_file))
                            if (stats['newest'] is None or 
                                file_time > stats['newest'][0]):
                                stats['newest'] = (file_time, str(backup_file))
                    
                    stats['by_date'][date_dir.name] = date_stats
                    stats['total_backups'] += date_stats['count']
                    stats['total_size'] += date_stats['size']
                    
        except Exception as e:
            logger.error(f"Erreur calcul stats: {e}")
        
        # Convertir la taille en format lisible
        stats['total_size_human'] = self._human_readable_size(stats['total_size'])
        
        return stats
    
    @staticmethod
    def _human_readable_size(size_bytes: int) -> str:
        """Convertit une taille en format lisible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

# Instance globale
backup_manager = BackupManager()
