"""
Lecture et écriture des fichiers de sauvegarde .save
"""

import struct
import zlib
import json
from pathlib import Path
from typing import BinaryIO, Optional
from dataclasses import asdict
from .data_models import GameSave, City, Vehicle, Industry
from utils.logger import get_logger

logger = get_logger(__name__)

class SaveFileManager:
    """Gère les opérations sur les fichiers de sauvegarde"""
    
    def __init__(self):
        self.current_save: Optional[GameSave] = None
        self.raw_data: Optional[bytearray] = None
        
        # Offsets connus (à découvrir et compléter)
        self.known_offsets = {
            'file_header': {'offset': 0x00, 'size': 4, 'description': 'En-tête fichier'},
            'game_version': {'offset': 0x10, 'size': 32, 'description': 'Version jeu'},
            'money_offset': {'offset': 0x1234, 'size': 8, 'type': '<q', 'description': 'Argent'},
            'map_size': {'offset': 0x200, 'size': 8, 'type': '<II', 'description': 'Taille carte'},
        }
    
    def load_save_file(self, filepath: str) -> Optional[GameSave]:
        """Charge un fichier de sauvegarde"""
        try:
            logger.info(f"Chargement: {filepath}")
            
            # Lecture du fichier binaire
            with open(filepath, 'rb') as f:
                self.raw_data = bytearray(f.read())
            
            # Création de l'objet GameSave
            self.current_save = self._parse_save_data(filepath)
            
            # Extraction basique des données
            self._extract_basic_info()
            
            logger.info(f"Sauvegarde chargée: {len(self.raw_data)} octets")
            return self.current_save
            
        except Exception as e:
            logger.error(f"Erreur chargement: {e}")
            return None
    
    def _extract_basic_info(self):
        """Extrait les informations de base du fichier"""
        if not self.current_save or not self.raw_data:
            return
        
        # Tenter de lire l'argent si on connaît l'offset
        try:
            money_offset = self.known_offsets['money_offset']['offset']
            money_data = self.raw_data[money_offset:money_offset+8]
            self.current_save.money = struct.unpack('<q', money_data)[0]
            logger.info(f"Argent trouvé: {self.current_save.money}")
        except:
            # On cherche dynamiquement
            self.current_save.money = self._find_money()
    
    def _find_money(self) -> int:
        """Cherche automatiquement la valeur de l'argent"""
        # Méthode 1: Cherche des valeurs qui ressemblent à de l'argent
        patterns = [
            (b'\x00\x00\x00\x00\x00\x00\x00\x00', 8),  # Zéro
            (b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF', 8),  # -1
        ]
        
        for i in range(0, len(self.raw_data) - 8, 8):
            chunk = bytes(self.raw_data[i:i+8])
            # Vérifie si c'est un nombre raisonnable (entre -1M et 10B)
            try:
                value = struct.unpack('<q', chunk)[0]
                if -1000000 < value < 10000000000:
                    # Vérifie que les 8 octets suivants sont différents
                    next_chunk = bytes(self.raw_data[i+8:i+16])
                    if chunk != next_chunk:
                        logger.debug(f"Candidat argent à 0x{i:08X}: {value}")
                        return value
            except:
                continue
        
        return 0
    
    def save_to_file(self, filepath: str, backup: bool = True) -> bool:
        """Sauvegarde les modifications dans un fichier"""
        try:
            if backup:
                self._create_backup(filepath)
            
            # Appliquer les modifications à raw_data
            self._apply_changes()
            
            # Écrire le fichier
            with open(filepath, 'wb') as f:
                f.write(self.raw_data)
            
            logger.info(f"Sauvegardé: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde: {e}")
            return False
    
    def _create_backup(self, original_path: str):
        """Crée une copie de sauvegarde"""
        backup_path = f"{original_path}.backup_{int(time.time())}"
        import shutil
        shutil.copy2(original_path, backup_path)
        logger.info(f"Backup créé: {backup_path}")
    
    def _apply_changes(self):
        """Applique toutes les modifications en attente"""
        if not self.current_save or not self.raw_data:
            return
        
        # Mettre à jour l'argent
        if 'money_offset' in self.known_offsets:
            offset = self.known_offsets['money_offset']['offset']
            money_bytes = struct.pack('<q', self.current_save.money)
            self.raw_data[offset:offset+8] = money_bytes
    
    def export_to_json(self, filepath: str):
        """Exporte les données au format JSON (pour debug)"""
        if not self.current_save:
            return
        
        data = asdict(self.current_save)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Export JSON: {filepath}")
