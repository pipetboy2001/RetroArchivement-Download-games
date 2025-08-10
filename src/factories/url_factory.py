"""
Factory para crear generadores de URL según la consola/plataforma.
"""
from urllib.parse import quote

from ..core.interfaces import URLGenerator


def _normalize_slashes(path: str) -> str:
    """Normaliza separadores a '/' y quita un '/' inicial si existe."""
    return path.replace("\\", "/").lstrip("/")


def _encode_rel_path(path: str) -> str:
    """Codifica el path relativo preservando '/'.

    - Espacios, paréntesis y otros caracteres especiales se codifican.
    - No codifica '/', '-', '_', '.' para URLs más limpias.
    """
    return quote(path, safe="/-_.")


def _strip_first_segment_if_matches(path: str, segment: str) -> str:
    """Si el path comienza con 'segment/', elimina ese primer segmento.

    Útil para evitar duplicar carpetas de consola cuando la BASE_URL ya
    incluye dicha carpeta (ej. 'PlayStation 2/').
    """
    norm = _normalize_slashes(path)
    seg_lower = segment.lower()
    if norm.lower().startswith(seg_lower + "/"):
        # Quitar exactamente el primer segmento (hasta el primer '/')
        return norm.split("/", 1)[1]
    return norm


class SNESURLGenerator(URLGenerator):
    """Generador de URLs para SNES/Super Famicom."""
    
    BASE_URL = "https://archive.org/download/retroachievements_collection_SNES-Super_Famicom/"
    
    def generate_url(self, rom_path: str) -> str:
        rel = _normalize_slashes(rom_path)
        return self.BASE_URL + _encode_rel_path(rel)
    
    def can_handle(self, rom_path: str) -> bool:
        return "SNES-Super Famicom" in rom_path


class NESURLGenerator(URLGenerator):
    """Generador de URLs para NES/Famicom."""
    
    BASE_URL = "https://archive.org/download/retroachievements_collection_NES-Famicom/"
    
    def generate_url(self, rom_path: str) -> str:
        rel = _normalize_slashes(rom_path)
        return self.BASE_URL + _encode_rel_path(rel)
    
    def can_handle(self, rom_path: str) -> bool:
        return "NES-Famicom" in rom_path


class PSPURLGenerator(URLGenerator):
    """Generador de URLs para PlayStation Portable."""
    
    BASE_URL = "https://dn720005.ca.archive.org/0/items/retroachievements_collection_PlayStation_Portable/PlayStation%20Portable/"
    
    def generate_url(self, rom_path: str) -> str:
        # La BASE_URL ya incluye 'PlayStation%20Portable/'
        rel = _strip_first_segment_if_matches(rom_path, "PlayStation Portable")
        return self.BASE_URL + _encode_rel_path(rel)
    
    def can_handle(self, rom_path: str) -> bool:
        return "PlayStation Portable" in rom_path


class PS1URLGenerator(URLGenerator):
    """Generador de URLs para PlayStation 1."""
    
    BASE_URL = "https://archive.org/download/retroachievements_collection_PlayStation/PlayStation/"
    
    def generate_url(self, rom_path: str) -> str:
        # La BASE_URL ya incluye 'PlayStation/'
        rel = _strip_first_segment_if_matches(rom_path, "PlayStation")
        return self.BASE_URL + _encode_rel_path(rel)
    
    def can_handle(self, rom_path: str) -> bool:
        return "PlayStation" in rom_path and "PlayStation 2" not in rom_path and "PlayStation Portable" not in rom_path


class PS2URLGenerator(URLGenerator):
    """Generador de URLs para PlayStation 2."""
    
    BASE_URL_A_M = "https://archive.org/download/retroachievements_collection_PlayStation_2_A-M/PlayStation%202/"
    BASE_URL_N_Z = "https://archive.org/download/retroachievements_collection_PlayStation_2_N-Z/PlayStation%202/"
    
    def generate_url(self, rom_path: str) -> str:
        # Quitar prefijo 'PlayStation 2/' si está presente para evitar duplicados
        rel = _strip_first_segment_if_matches(rom_path, "PlayStation 2")
        # Decidir entre A-M o N-Z basado en el nombre del archivo (primer caracter)
        game_name = rel.split('/')[-1] if '/' in rel else rel
        base = self.BASE_URL_A_M if (game_name and game_name[0].upper() < 'N') else self.BASE_URL_N_Z
        return base + _encode_rel_path(rel)
    
    def can_handle(self, rom_path: str) -> bool:
        return "PlayStation 2" in rom_path


class SegaURLGenerator(URLGenerator):
    """Generador de URLs para consolas Sega (Genesis, Mega Drive, Sega CD)."""
    
    BASE_URL = "https://archive.org/download/retroachievements_collection_v5/"
    
    def generate_url(self, rom_path: str) -> str:
        rel = _normalize_slashes(rom_path)
        return self.BASE_URL + _encode_rel_path(rel)
    
    def can_handle(self, rom_path: str) -> bool:
        return any(console in rom_path for console in ["Genesis-Mega Drive", "Sega CD"])


class ArcadeURLGenerator(URLGenerator):
    """Generador de URLs para Arcade."""
    
    BASE_URL = "https://archive.org/download/fbnarcade-fullnonmerged/arcade/"
    
    def generate_url(self, rom_path: str) -> str:
        rel = _normalize_slashes(rom_path)
        return self.BASE_URL + _encode_rel_path(rel)
    
    def can_handle(self, rom_path: str) -> bool:
        return "Arcade" in rom_path


class DefaultURLGenerator(URLGenerator):
    """Generador de URLs por defecto."""
    
    BASE_URL = "https://archive.org/download/retroachievements_collection_v5/"
    
    def generate_url(self, rom_path: str) -> str:
        rel = _normalize_slashes(rom_path)
        return self.BASE_URL + _encode_rel_path(rel)
    
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
