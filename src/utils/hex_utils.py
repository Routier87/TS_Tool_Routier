"""
Utilitaires pour la manipulation hexadécimale
"""

import struct
import binascii
from typing import Union, List, Tuple, Optional

class HexUtils:
    """Classe utilitaire pour les opérations hexadécimales"""
    
    @staticmethod
    def bytes_to_hex(data: bytes, spaces: bool = True, uppercase: bool = True) -> str:
        """
        Convertit des bytes en string hexadécimale
        
        Args:
            data: Bytes à convertir
            spaces: Ajouter des espaces entre les bytes
            uppercase: Utiliser des lettres majuscules
            
        Returns:
            String hexadécimale
        """
        hex_str = binascii.hexlify(data).decode('ascii')
        if uppercase:
            hex_str = hex_str.upper()
        
        if spaces:
            # Ajouter un espace tous les 2 caractères
            hex_str = ' '.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))
        
        return hex_str
    
    @staticmethod
    def hex_to_bytes(hex_str: str) -> bytes:
        """
        Convertit une string hexadécimale en bytes
        
        Args:
            hex_str: String hexadécimale (avec ou sans espaces)
            
        Returns:
            Bytes convertis
        """
        # Supprimer les espaces et le préfixe 0x
        hex_str = hex_str.replace(' ', '').replace('0x', '')
        
        # Ajouter un 0 si longueur impaire
        if len(hex_str) % 2 != 0:
            hex_str = '0' + hex_str
        
        return binascii.unhexlify(hex_str)
    
    @staticmethod
    def format_hex_dump(data: bytes, offset: int = 0, bytes_per_line: int = 16) -> str:
        """
        Formate des bytes en dump hexadécimal classique
        
        Args:
            data: Bytes à formater
            offset: Offset de départ pour l'affichage
            bytes_per_line: Nombre de bytes par ligne
            
        Returns:
            String formatée
        """
        result = []
        
        for i in range(0, len(data), bytes_per_line):
            chunk = data[i:i + bytes_per_line]
            
            # Offset
            line = f"{offset + i:08X}: "
            
            # Hex
            hex_part = ' '.join(f"{b:02X}" for b in chunk)
            hex_part = hex_part.ljust(bytes_per_line * 3)
            
            # ASCII
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            
            result.append(f"{line}{hex_part}  {ascii_part}")
        
        return '\n'.join(result)
    
    @staticmethod
    def find_pattern(data: bytes, pattern: bytes, start_offset: int = 0) -> List[int]:
        """
        Trouve toutes les occurrences d'un pattern dans des bytes
        
        Args:
            data: Bytes dans lesquels chercher
            pattern: Pattern à trouver
            start_offset: Offset de départ pour la recherche
            
        Returns:
            Liste des offsets où le pattern a été trouvé
        """
        offsets = []
        pos = data.find(pattern, start_offset)
        
        while pos != -1:
            offsets.append(pos)
            pos = data.find(pattern, pos + 1)
        
        return offsets
    
    @staticmethod
    def read_int(data: bytes, offset: int, size: int = 4, signed: bool = False, 
                 little_endian: bool = True) -> int:
        """
        Lit un entier depuis des bytes
        
        Args:
            data: Bytes source
            offset: Position de départ
            size: Taille en bytes (1, 2, 4, 8)
            signed: True pour un entier signé
            little_endian: True pour little-endian, False pour big-endian
            
        Returns:
            Entier lu
        """
        endian = '<' if little_endian else '>'
        
        fmt_map = {
            1: 'b' if signed else 'B',
            2: 'h' if signed else 'H',
            4: 'i' if signed else 'I',
            8: 'q' if signed else 'Q'
        }
        
        if size not in fmt_map:
            raise ValueError(f"Taille non supportée: {size}")
        
        fmt = endian + fmt_map[size]
        return struct.unpack_from(fmt, data, offset)[0]
    
    @staticmethod
    def write_int(value: int, size: int = 4, signed: bool = False, 
                  little_endian: bool = True) -> bytes:
        """
        Écrit un entier en bytes
        
        Args:
            value: Valeur à écrire
            size: Taille en bytes
            signed: True pour un entier signé
            little_endian: True pour little-endian
            
        Returns:
            Bytes représentant l'entier
        """
        endian = '<' if little_endian else '>'
        
        fmt_map = {
            1: 'b' if signed else 'B',
            2: 'h' if signed else 'H',
            4: 'i' if signed else 'I',
            8: 'q' if signed else 'Q'
        }
        
        if size not in fmt_map:
            raise ValueError(f"Taille non supportée: {size}")
        
        fmt = endian + fmt_map[size]
        return struct.pack(fmt, value)
    
    @staticmethod
    def read_string(data: bytes, offset: int, encoding: str = 'utf-8', 
                    max_length: Optional[int] = None) -> Tuple[str, int]:
        """
        Lit une string null-terminated
        
        Args:
            data: Bytes source
            offset: Position de départ
            encoding: Encodage de la string
            max_length: Longueur maximale à lire
            
        Returns:
            Tuple (string, bytes_lus)
        """
        end = offset
        max_end = len(data) if max_length is None else min(offset + max_length, len(data))
        
        while end < max_end and data[end] != 0:
            end += 1
        
        string_data = data[offset:end]
        try:
            return string_data.decode(encoding), end - offset + 1
        except UnicodeDecodeError:
            # Fallback sur latin-1
            return string_data.decode('latin-1'), end - offset + 1
    
    @staticmethod
    def calculate_checksum(data: bytes) -> int:
        """
        Calcule une checksum simple (somme des bytes)
        
        Args:
            data: Bytes pour lesquels calculer la checksum
            
        Returns:
            Checksum (0-255)
        """
        return sum(data) & 0xFF

# Instance globale pour usage simple
hex_utils = HexUtils()
