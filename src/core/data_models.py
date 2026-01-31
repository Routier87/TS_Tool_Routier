"""
Modèles de données pour Transport Fever 2
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class GameSave:
    """Représente une sauvegarde complète du jeu"""
    filename: str
    filepath: str
    file_size: int
    game_version: str
    timestamp: datetime
    money: int = 0
    difficulty: str = "Normal"
    
    # Entités du jeu
    cities: List['City'] = field(default_factory=list)
    vehicles: List['Vehicle'] = field(default_factory=list)
    industries: List['Industry'] = field(default_factory=list)
    lines: List['TransportLine'] = field(default_factory=list)
    
    # Métadonnées
    map_size: tuple = (512, 512)  # largeur, hauteur
    map_seed: int = 0
    campaign_progress: int = 0
    
    def __str__(self):
        return (f"Save: {self.filename}\n"
                f"Argent: {self.money:,} €\n"
                f"Villes: {len(self.cities)}\n"
                f"Véhicules: {len(self.vehicles)}")

@dataclass
class City:
    """Représente une ville dans le jeu"""
    id: int
    name: str
    x: float  # Coordonnée X sur la carte
    y: float  # Coordonnée Y sur la carte
    population: int = 1000
    growth_rate: float = 1.0
    connected_industries: List[int] = field(default_factory=list)
    
    # Ressources disponibles
    resources: Dict[str, int] = field(default_factory=dict)
    
    def get_position(self):
        return (self.x, self.y)

@dataclass
class Vehicle:
    """Représente un véhicule (train, camion, bateau, avion)"""
    id: int
    name: str
    vehicle_type: str  # "train", "truck", "ship", "plane"
    model: str  # Nom du modèle
    year: int  # Année d'introduction
    
    # Statistiques
    speed: float = 80.0  # km/h
    power: float = 1000.0  # kW
    capacity: int = 100  # Nombre de passagers/tonnes
    
    # Position et état
    x: float = 0.0
    y: float = 0.0
    line_id: Optional[int] = None  # Ligne à laquelle il est assigné
    maintenance_state: float = 1.0  # État de maintenance (0.0 à 1.0)
    
    # Coûts
    purchase_cost: int = 100000
    running_cost: int = 1000

@dataclass
class Industry:
    """Représente une industrie ou une ressource"""
    id: int
    name: str
    industry_type: str  # "oil", "coal", "farm", "factory", etc.
    x: float
    y: float
    production_rate: float = 1.0
    connected_to: List[int] = field(default_factory=list)  # IDs des villes connectées

@dataclass  
class TransportLine:
    """Représente une ligne de transport"""
    id: int
    name: str
    transport_type: str  # "train", "truck", "ship", "plane"
    stops: List[Dict] = field(default_factory=list)  # Liste des arrêts
    vehicles: List[int] = field(default_factory=list)  # IDs des véhicules assignés
    profit: int = 0  Profit mensuel
