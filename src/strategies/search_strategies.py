"""
Estrategias para diferentes modos de búsqueda de juegos.
"""
from typing import Optional, List, Dict, Any
import json
from rich.console import Console
from rich.prompt import Prompt

from ..core.interfaces import HashSearchStrategy, GameInfo
from ..core.data_manager import RetroAchievementsDataManager


class DirectHashSearchStrategy(HashSearchStrategy):
    """Estrategia para búsqueda directa por hash."""
    
    def __init__(self):
        self.console = Console()
        self.data_manager = RetroAchievementsDataManager()
    
    def search(self, hash_value: str) -> Optional[GameInfo]:
        """Busca un juego por su hash directamente."""
        rom_path = self.data_manager.find_hash(hash_value)
        
        if rom_path:
            # Extraer información básica del rom_path
            console_name = self._extract_console_name(rom_path)
            game_name = self._extract_game_name(rom_path)
            
            return GameInfo(
                name=game_name,
                console=console_name,
                hash_value=hash_value,
                rom_path=rom_path
            )
        return None
    
    def _extract_console_name(self, rom_path: str) -> str:
        """Extrae el nombre de la consola del rom_path."""
        if "SNES-Super Famicom" in rom_path:
            return "SNES"
        elif "NES-Famicom" in rom_path:
            return "NES"
        elif "PlayStation Portable" in rom_path:
            return "PSP"
        elif "PlayStation 2" in rom_path:
            return "PS2"
        elif "PlayStation" in rom_path:
            return "PS1"
        elif "Genesis-Mega Drive" in rom_path:
            return "Genesis"
        elif "Sega CD" in rom_path:
            return "Sega CD"
        elif "Arcade" in rom_path:
            return "Arcade"
        else:
            return "Unknown"
    
    def _extract_game_name(self, rom_path: str) -> str:
        """Extrae el nombre del juego del rom_path."""
        # Tomar el último elemento del path como nombre del juego
        return rom_path.split('/')[-1] if '/' in rom_path else rom_path


class WantToPlaySearchStrategy(HashSearchStrategy):
    """Estrategia para búsqueda desde lista de deseos."""
    
    def __init__(self, want_to_play_file: str = None):
        self.console = Console()
        # Usar configuración centralizada si no se especifica archivo
        if want_to_play_file is None:
            try:
                import config
                self.want_to_play_file = config.WANT_TO_PLAY_FILE
                self.PREFERRED_REGIONS = config.PREFERRED_REGIONS
            except ImportError:
                self.want_to_play_file = "game_hashes.json"
                self.PREFERRED_REGIONS = {
                    "ES": 1, "USA": 2, "WORLD": 3, "EUROPE": 4, "JPN": 5
                }
        else:
            self.want_to_play_file = want_to_play_file
            self.PREFERRED_REGIONS = {
                "ES": 1, "USA": 2, "WORLD": 3, "EUROPE": 4, "JPN": 5
            }
        self.data_manager = RetroAchievementsDataManager()
        self.missing_games = []
    
    def search(self, game_identifier: str) -> Optional[GameInfo]:
        """Busca un juego desde la lista de deseos."""
        try:
            with open(self.want_to_play_file, 'r', encoding='utf-8') as f:
                want_to_play_data = json.load(f)
        except Exception as e:
            self.console.print(f"[bold red]Error al cargar {self.want_to_play_file}: {e}[/bold red]")
            return None
        
        if game_identifier in want_to_play_data:
            game_data = want_to_play_data[game_identifier]
            hash_value = self._select_best_hash(game_data)
            
            if hash_value:
                rom_path = self.data_manager.find_hash(hash_value)
                if rom_path:
                    return GameInfo(
                        name=game_identifier,
                        console=game_data.get("console", "Unknown"),
                        hash_value=hash_value,
                        rom_path=rom_path,
                        region=self._get_selected_region(game_data, hash_value)
                    )
        
        return None
    
    def _select_best_hash(self, game_data: Dict[str, Any]) -> Optional[str]:
        """Selecciona el mejor hash basado en las preferencias de región."""
        regions = game_data.get("regions", {})
        if not regions:
            return None
        
        # Buscar región preferida
        selected_region = None
        for preferred_region in self.PREFERRED_REGIONS:
            if preferred_region.upper() in regions:
                selected_region = preferred_region.upper()
                break
        
        if not selected_region:
            selected_region = list(regions.keys())[0]
        
        hashes = regions[selected_region]
        
        # Buscar hash preferido dentro de la región
        for hash_data in hashes:
            if any(preference in hash_data.get('name', '').upper() 
                   for preference in self.PREFERRED_REGIONS.keys()):
                return hash_data.get('hash')
        
        # Si no se encuentra un hash preferido, tomar el primero
        if hashes:
            return hashes[0].get('hash')
        
        return None
    
    def _get_selected_region(self, game_data: Dict[str, Any], hash_value: str) -> Optional[str]:
        """Obtiene la región del hash seleccionado."""
        regions = game_data.get("regions", {})
        for region, hashes in regions.items():
            for hash_data in hashes:
                if hash_data.get('hash') == hash_value:
                    return region
        return None
    
    def get_available_consoles(self) -> List[str]:
        """Obtiene lista de consolas disponibles en la lista de deseos."""
        try:
            with open(self.want_to_play_file, 'r', encoding='utf-8') as f:
                want_to_play_data = json.load(f)
            
            consoles = set()
            for game_data in want_to_play_data.values():
                console_name = game_data.get("console")
                if console_name:
                    consoles.add(console_name)
            return list(consoles)
        except Exception as e:
            self.console.print(f"[bold red]Error al cargar consolas: {e}[/bold red]")
            return []
    
    def get_games_for_console(self, console_name: str) -> List[str]:
        """Obtiene lista de juegos para una consola específica."""
        try:
            with open(self.want_to_play_file, 'r', encoding='utf-8') as f:
                want_to_play_data = json.load(f)
            
            games = []
            for game_name, game_data in want_to_play_data.items():
                if game_data.get("console") == console_name:
                    games.append(game_name)
            return games
        except Exception as e:
            self.console.print(f"[bold red]Error al cargar juegos: {e}[/bold red]")
            return []
