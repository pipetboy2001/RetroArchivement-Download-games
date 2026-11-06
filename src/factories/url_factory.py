"""
Factory para crear generadores de URL según la consola/plataforma.
"""
import json
from typing import Dict
from urllib.parse import quote

from ..core.interfaces import URLGenerator

_source_override_cache: Dict[str, dict] = {}


def _load_source_override(path: str) -> dict:
    """Carga (y cachea en memoria) un Data/<consola>_source_override.json
    generado por sync_source.py -- mapea rom_path -> nombre de archivo en
    la colección de reemplazo. Si no existe todavía, devuelve {} (la
    consola sigue usando su BASE_URL de siempre, sin romper nada)."""
    if path not in _source_override_cache:
        try:
            with open(path, encoding="utf-8") as f:
                _source_override_cache[path] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            _source_override_cache[path] = {}
    return _source_override_cache[path]


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
    """Generador de URLs para SNES/Super Famicom.

    La colección vieja de archive.org (BASE_URL) murió. Hay una de
    reemplazo, pero con nombres/estructura distintos -- sync_source.py
    genera Data/snes_source_override.json (rom_path -> nombre de archivo
    en la colección nueva) matcheando por hash real, no por nombre. Lo que
    todavía no tiene match sigue cayendo en el BASE_URL viejo (roto, pero
    es justo lo que queda listado en Data/snes_missing_sources.txt)."""

    BASE_URL = "https://archive.org/download/retroachievements_collection_SNES-Super_Famicom/"
    BASE_URL_REPLACEMENT = "https://archive.org/download/retroachievementscompatibleromsSNES/"
    OVERRIDE_FILE = "Data/snes_source_override.json"

    def generate_url(self, rom_path: str) -> str:
        rel = _normalize_slashes(rom_path)
        override = _load_source_override(self.OVERRIDE_FILE)
        filename = override.get(rel)
        if filename:
            return self.BASE_URL_REPLACEMENT + _encode_rel_path(filename)
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
    """Generador de URLs para Arcade.

    Bug encontrado (no es un problema de fuente muerta, como SNES): los
    rom_path reales usan "arcade\\" en minúscula (ej. "arcade\\sailormn.zip"),
    pero can_handle() comparaba contra "Arcade" con mayúscula -- ningún
    juego de Arcade pasaba nunca por este generador, caían todos en el
    DefaultURLGenerator (BASE_URL de v5, rotos). Y aunque entraran, BASE_URL
    ya termina en ".../arcade/" y el rom_path también empieza con
    "arcade/", así que sin strip quedaba duplicado
    (".../arcade/arcade/...", también roto). Confirmado con la colección
    real: https://archive.org/download/fbnarcade-fullnonmerged/arcade/<archivo>
    sí funciona."""

    BASE_URL = "https://archive.org/download/fbnarcade-fullnonmerged/arcade/"

    def generate_url(self, rom_path: str) -> str:
        rel = _strip_first_segment_if_matches(rom_path, "arcade")
        return self.BASE_URL + _encode_rel_path(rel)

    def can_handle(self, rom_path: str) -> bool:
        first_segment = _normalize_slashes(rom_path).split("/", 1)[0]
        return first_segment.lower() == "arcade"


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
