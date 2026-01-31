"""
Système de logging pour TS_Tool_Routier
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import os

class ColorFormatter(logging.Formatter):
    """Formatter avec couleurs pour la console"""
    
    COLORS = {
        'DEBUG': '\033[94m',      # Bleu
        'INFO': '\033[92m',       # Vert
        'WARNING': '\033[93m',    # Jaune
        'ERROR': '\033[91m',      # Rouge
        'CRITICAL': '\033[95m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        log_message = super().format(record)
        if sys.stdout.isatty():  # Seulement si console supporte couleurs
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            return f"{color}{log_message}{self.COLORS['RESET']}"
        return log_message

def setup_logger(log_level=logging.INFO, log_to_file=True):
    """
    Configure le système de logging
    
    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, etc.)
        log_to_file: Si True, écrit aussi dans un fichier
    """
    # Créer le logger principal
    logger = logging.getLogger("TS_Tool_Routier")
    logger.setLevel(log_level)
    
    # Éviter les logs multiples
    if logger.handlers:
        return logger
    
    # Formatter standard
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Handler console avec couleurs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    color_formatter = ColorFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)
    
    # Handler fichier
    if log_to_file:
        # Créer dossier logs si inexistant
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Fichier avec date
        log_file = log_dir / f"ts_tool_{datetime.now():%Y%m%d}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Tout logger dans le fichier
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name=None):
    """
    Retourne un logger
    
    Args:
        name: Nom du logger (si None, retourne le logger principal)
    """
    if name:
        return logging.getLogger(f"TS_Tool_Routier.{name}")
    return logging.getLogger("TS_Tool_Routier")
