"""
Factory para crear generadores de URL según la consola/plataforma.
"""
from typing import List
from urllib.parse import quote

from ..core.interfaces import URLGenerator


class SNESURLGenerator(URLGenerator):
    """Generador de URLs para SNES/Super Famicom."""
    
    BASE_URL = "https://archive.org/download/retroachievements_collection_SNES-Super_Famicom/"
    
    def generate_url(self, rom_path: str) -> str:
        return self.BASE_URL + rom_path.replace("\\", "/").replace(" ", "%20")
    
    def can_handle(self, rom_path: str) -> bool:
        return "SNES-Super Famicom" in rom_path


class NESURLGenerator(URLGenerator):
    """Generador de URLs para NES/Famicom."""
    
    BASE_URL = "https://archive.org/download/retroachievements_collection_NES-Famicom/"
    
    def generate_url(self, rom_path: str) -> str:
        return self.BASE_URL + rom_path.replace("\\", "/").replace(" ", "%20")
    
    def can_handle(self, rom_path: str) -> bool:
        return "NES-Famicom" in rom_path


class PSPURLGenerator(URLGenerator):
    """Generador de URLs para PlayStation Portable."""
    
    BASE_URL = "https://dn720005.ca.archive.org/0/items/retroachievements_collection_PlayStation_Portable/PlayStation%20Portable/"
    
    def generate_url(self, rom_path: str) -> str:
        return self.BASE_URL + rom_path.replace("\\", "/").replace(" ", "%20")
    
    def can_handle(self, rom_path: str) -> bool:
        return "PlayStation Portable" in rom_path


class PS1URLGenerator(URLGenerator):
    """Generador de URLs para PlayStation 1."""
    
    BASE_URL = "https://archive.org/download/retroachievements_collection_PlayStation/PlayStation/"
    
    def generate_url(self, rom_path: str) -> str:
        return self.BASE_URL + rom_path.replace("\\", "/").replace(" ", "%20")
    
    def can_handle(self, rom_path: str) -> bool:
        return "PlayStation" in rom_path and "PlayStation 2" not in rom_path and "PlayStation Portable" not in rom_path


class PS2URLGenerator(URLGenerator):
    """Generador de URLs para PlayStation 2."""
    
    BASE_URL_A_M = "https://archive.org/download/retroachievements_collection_PlayStation_2_A-M/PlayStation%202/"
    BASE_URL_N_Z = "https://archive.org/download/retroachievements_collection_PlayStation_2_N-Z/PlayStation%202/"
    
    def generate_url(self, rom_path: str) -> str:
        # Decidir entre A-M o N-Z basado en el nombre del juego
        game_name = rom_path.split('/')[-1] if '/' in rom_path else rom_path
        if game_name and game_name[0].upper() < 'N':
            return self.BASE_URL_A_M + rom_path.replace("\\", "/").replace(" ", "%20")
        else:
            return self.BASE_URL_N_Z + rom_path.replace("\\", "/").replace(" ", "%20")
    
    def can_handle(self, rom_path: str) -> bool:
        return "PlayStation 2" in rom_path


class SegaURLGenerator(URLGenerator):
    """Generador de URLs para consolas Sega (Genesis, Mega Drive, Sega CD)."""
    
    BASE_URL = "https://archive.org/download/retroachievements_collection_v5/"
    
    def generate_url(self, rom_path: str) -> str:
        return self.BASE_URL + rom_path.replace("\\", "/").replace(" ", "%20")
    
    def can_handle(self, rom_path: str) -> bool:
        return any(console in rom_path for console in ["Genesis-Mega Drive", "Sega CD"])


class ArcadeURLGenerator(URLGenerator):
    """Generador de URLs para Arcade."""
    
    BASE_URL = "https://archive.org/download/fbnarcade-fullnonmerged/arcade/"
    
    def generate_url(self, rom_path: str) -> str:
        return self.BASE_URL + rom_path.replace("\\", "/").replace(" ", "%20")
    
    def can_handle(self, rom_path: str) -> bool:
        return "Arcade" in rom_path


class DefaultURLGenerator(URLGenerator):
    """Generador de URLs por defecto."""
    
    BASE_URL = "https://archive.org/download/retroachievements_collection_v5/"
    
    def generate_url(self, rom_path: str) -> str:
        return self.BASE_URL + rom_path.replace("\\", "/").replace(" ", "%20")
    
    def can_handle(self, rom_path: str) -> bool:
        return True  # Siempre puede manejar como fallback


class URLGeneratorFactory:
    """Factory para crear generadores de URL."""
    
    _generators = [
        SNESURLGenerator(),
        NESURLGenerator(),
        PSPURLGenerator(),
        PS1URLGenerator(),
        PS2URLGenerator(),
        SegaURLGenerator(),
        ArcadeURLGenerator(),
        DefaultURLGenerator()  # Debe ir al final como fallback
    ]
    
    @classmethod
    def get_generator(cls, rom_path: str) -> URLGenerator:
        """Obtiene el generador apropiado para la ROM."""
        for generator in cls._generators:
            if generator.can_handle(rom_path):
                return generator
        return cls._generators[-1]  # Retorna el generador por defecto
    
    @classmethod
    def generate_url(cls, rom_path: str) -> str:
        """Genera la URL de descarga para una ROM."""
        generator = cls.get_generator(rom_path)
        return generator.generate_url(rom_path)
