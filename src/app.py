"""
Aplicación principal que maneja ambos modos de operación.
"""
from typing import Optional, List
from enum import Enum

from .core.interfaces import HashSearchStrategy, GameInfo
from .strategies.search_strategies import DirectHashSearchStrategy, WantToPlaySearchStrategy
from .commands.download_commands import OpenInBrowserCommand, BatchDownloadCommand, DisplayURLCommand
from .utils.helpers import UIHelper, ValidationHelper


class AppMode(Enum):
    """Modos de operación de la aplicación."""
    DIRECT_HASH = "direct_hash"
    WANT_TO_PLAY = "want_to_play"


class RetroAchievementsDownloader:
    """Aplicación principal para descarga de ROMs de RetroAchievements."""
    
    def __init__(self, mode: AppMode = AppMode.DIRECT_HASH):
        self.mode = mode
        self.ui_helper = UIHelper()
        self.search_strategy: Optional[HashSearchStrategy] = None
        self._setup_strategy()
    
    def _setup_strategy(self):
        """Configura la estrategia de búsqueda según el modo."""
        if self.mode == AppMode.DIRECT_HASH:
            self.search_strategy = DirectHashSearchStrategy()
        elif self.mode == AppMode.WANT_TO_PLAY:
            self.search_strategy = WantToPlaySearchStrategy()
    
    def run(self):
        """Ejecuta la aplicación en el modo configurado."""
        self.ui_helper.display_welcome_message("RetroAchievements Downloader")
        
        if self.mode == AppMode.DIRECT_HASH:
            self._run_direct_hash_mode()
        elif self.mode == AppMode.WANT_TO_PLAY:
            self._run_want_to_play_mode()
    
    def _run_direct_hash_mode(self):
        """Ejecuta el modo de búsqueda directa por hash."""
        self.ui_helper.display_info_message("Modo: Búsqueda directa por hash")
        
        while True:
            hash_value = self.ui_helper.get_hash_input()
            if hash_value is None:  # Usuario eligió salir
                break
            
            if not ValidationHelper.is_valid_hash(hash_value):
                self.ui_helper.display_error_message("Hash inválido. Debe ser hexadecimal y tener al menos 8 caracteres.")
                continue
            
            game_info = self.search_strategy.search(hash_value)
            
            if game_info:
                command = OpenInBrowserCommand(game_info)
                command.execute()
            else:
                self.ui_helper.display_error_message(f"Hash {hash_value} no encontrado en el archivo JSON.")
    
    def _run_want_to_play_mode(self):
        """Ejecuta el modo de lista de deseos."""
        self.ui_helper.display_info_message("Modo: Lista de deseos")
        
        strategy = self.search_strategy
        
        # Seleccionar consola
        consoles = strategy.get_available_consoles()
        if not consoles:
            self.ui_helper.display_error_message("No se encontraron consolas en la lista de deseos.")
            return
        
        selected_console = self.ui_helper.select_from_list(consoles, "una consola")
        if not selected_console:
            return
        
        # Seleccionar juego(s)
        games = strategy.get_games_for_console(selected_console)
        if not games:
            self.ui_helper.display_error_message(f"No se encontraron juegos para {selected_console}.")
            return
        
        selected_game = self.ui_helper.select_from_list(games, "un juego", allow_all=True)
        if not selected_game:
            return
        
        # Procesar selección
        if selected_game == "todos":
            self._process_all_games(games)
        else:
            self._process_single_game(selected_game)
    
    def _process_single_game(self, game_name: str):
        """Procesa un solo juego."""
        game_info = self.search_strategy.search(game_name)
        
        if game_info:
            command = OpenInBrowserCommand(game_info)
            command.execute()
        else:
            self.ui_helper.display_error_message(f"No se pudo procesar el juego: {game_name}")
    
    def _process_all_games(self, game_names: List[str]):
        """Procesa todos los juegos de una consola."""
        games_info = []
        
        for game_name in game_names:
            game_info = self.search_strategy.search(game_name)
            if game_info:
                games_info.append(game_info)
            else:
                self.ui_helper.display_error_message(f"No se pudo procesar: {game_name}")
        
        if games_info:
            command = BatchDownloadCommand(games_info)
            command.execute()
        else:
            self.ui_helper.display_error_message("No se pudieron procesar los juegos seleccionados.")
    
    def search_hash(self, hash_value: str) -> Optional[GameInfo]:
        """Busca un hash específico (API pública)."""
        return self.search_strategy.search(hash_value)
    
    def set_mode(self, mode: AppMode):
        """Cambia el modo de operación."""
        self.mode = mode
        self._setup_strategy()


# Funciones de conveniencia para mantener compatibilidad
def create_direct_hash_app() -> RetroAchievementsDownloader:
    """Crea una instancia de la app en modo hash directo."""
    return RetroAchievementsDownloader(AppMode.DIRECT_HASH)


def create_want_to_play_app() -> RetroAchievementsDownloader:
    """Crea una instancia de la app en modo lista de deseos."""
    return RetroAchievementsDownloader(AppMode.WANT_TO_PLAY)
