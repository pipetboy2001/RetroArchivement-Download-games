"""
Singleton para el manejo de datos JSON de RetroAchievements.
"""
import json
from typing import Optional, Dict, Any
from pathlib import Path
from rich.console import Console

from .interfaces import DataProvider


class RetroAchievementsDataManager(DataProvider):
    """Singleton para manejar los datos de RetroAchievements."""
    
    _instance = None
    _data = None
    
    def __new__(cls, json_file_path: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Usar configuración centralizada si no se especifica path
            if json_file_path is None:
                try:
                    import config
                    cls._instance.json_file_path = config.JSON_FILE_PATH
                except ImportError:
                    cls._instance.json_file_path = "Data/TamperMonkeyRetroachievements.json"
            else:
                cls._instance.json_file_path = json_file_path
            cls._instance.console = Console()
        return cls._instance
    
    def load_data(self) -> Optional[Dict[str, Any]]:
        """Carga los datos del archivo JSON si no están ya cargados."""
        if self._data is None:
            try:
                with open(self.json_file_path, 'r', encoding='utf-8') as file:
                    self._data = json.load(file)
                self.console.print("[bold green]Datos JSON cargados exitosamente.[/bold green]")
            except FileNotFoundError:
                self.console.print(f"[bold red]Archivo JSON no encontrado: {self.json_file_path}[/bold red]")
                return None
            except json.JSONDecodeError as e:
                self.console.print(f"[bold red]Error al decodificar el archivo JSON: {e}[/bold red]")
                return None
            except Exception as e:
                self.console.print(f"[bold red]Error al cargar el archivo JSON: {e}[/bold red]")
                return None
        
        return self._data
    
    def reload_data(self) -> Optional[Dict[str, Any]]:
        """Fuerza la recarga de los datos."""
        self._data = None
        return self.load_data()
    
    def find_hash(self, hash_value: str) -> Optional[str]:
        """Busca un hash en los datos cargados."""
        data = self.load_data()
        if not data:
            return None
        
        hash_upper = hash_value.upper()
        for console_id, hash_list in data.items():
            for item in hash_list:
                if hash_upper in item:
                    return item[hash_upper]
        return None
