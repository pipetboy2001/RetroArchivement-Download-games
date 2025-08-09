"""
Comandos para operaciones de descarga.
"""
import webbrowser
from typing import List
from rich.console import Console

from ..core.interfaces import DownloadCommand, GameInfo
from ..factories.url_factory import URLGeneratorFactory


class OpenInBrowserCommand(DownloadCommand):
    """Comando para abrir URL en el navegador."""
    
    def __init__(self, game_info: GameInfo):
        self.game_info = game_info
        self.console = Console()
    
    def execute(self) -> bool:
        """Ejecuta la apertura en el navegador."""
        try:
            download_url = URLGeneratorFactory.generate_url(self.game_info.rom_path)
            
            self.console.print(
                f"Hash encontrado. La URL de descarga es: {download_url}", 
                style="bold green"
            )
            self.console.print(
                f"Abriendo [link]{download_url}[/link] en el navegador...", 
                style="bold blue"
            )
            
            webbrowser.open(download_url)
            return True
            
        except Exception as e:
            self.console.print(f"[bold red]Error al abrir en el navegador: {e}[/bold red]")
            return False


class BatchDownloadCommand(DownloadCommand):
    """Comando para descarga en lote."""
    
    def __init__(self, games: List[GameInfo]):
        self.games = games
        self.console = Console()
        self.missing_games = []
    
    def execute(self) -> bool:
        """Ejecuta la descarga en lote."""
        success_count = 0
        
        for game in self.games:
            command = OpenInBrowserCommand(game)
            if command.execute():
                success_count += 1
                self.console.print(f"✅ {game.name} procesado exitosamente")
            else:
                self.missing_games.append(game.name)
                self.console.print(f"❌ Error procesando {game.name}")
        
        # Guardar juegos faltantes si los hay
        if self.missing_games:
            self._save_missing_games()
        
        self.console.print(
            f"[bold green]Proceso completado: {success_count}/{len(self.games)} juegos procesados[/bold green]"
        )
        
        return success_count > 0
    
    def _save_missing_games(self):
        """Guarda la lista de juegos faltantes."""
        try:
            # Usar configuración centralizada para el nombre del archivo
            try:
                import config
                filename = config.MISSING_GAMES_FILE
            except ImportError:
                filename = "missing_games.txt"
                
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(self.missing_games) + "\n")
            self.console.print(
                f"[bold yellow]Lista de juegos faltantes guardada en {filename}[/bold yellow]"
            )
        except Exception as e:
            self.console.print(f"[bold red]Error guardando lista de juegos faltantes: {e}[/bold red]")


class DisplayURLCommand(DownloadCommand):
    """Comando para mostrar URL sin abrir navegador."""
    
    def __init__(self, game_info: GameInfo):
        self.game_info = game_info
        self.console = Console()
    
    def execute(self) -> bool:
        """Ejecuta la visualización de la URL."""
        try:
            download_url = URLGeneratorFactory.generate_url(self.game_info.rom_path)
            
            self.console.print(
                f"Hash encontrado. La URL de descarga es: {download_url}", 
                style="bold green"
            )
            
            return True
            
        except Exception as e:
            self.console.print(f"[bold red]Error generando URL: {e}[/bold red]")
            return False
