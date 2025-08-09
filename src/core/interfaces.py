"""
Interfaces y clases abstractas para el sistema de descarga de RetroAchievements.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class GameInfo:
    """Información de un juego."""
    name: str
    console: str
    hash_value: str
    rom_path: str
    region: Optional[str] = None


class HashSearchStrategy(ABC):
    """Estrategia abstracta para buscar hashes."""
    
    @abstractmethod
    def search(self, query: str) -> Optional[GameInfo]:
        """Busca un juego basado en la consulta."""
        pass


class URLGenerator(ABC):
    """Generador abstracto de URLs de descarga."""
    
    @abstractmethod
    def generate_url(self, rom_path: str) -> str:
        """Genera la URL de descarga para una ROM."""
        pass
    
    @abstractmethod
    def can_handle(self, rom_path: str) -> bool:
        """Determina si este generador puede manejar la ROM."""
        pass


class DataProvider(ABC):
    """Proveedor abstracto de datos."""
    
    @abstractmethod
    def load_data(self) -> Optional[Dict[str, Any]]:
        """Carga los datos necesarios."""
        pass


class DownloadCommand(ABC):
    """Comando abstracto para operaciones de descarga."""
    
    @abstractmethod
    def execute(self) -> bool:
        """Ejecuta el comando de descarga."""
        pass
