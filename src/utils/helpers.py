"""
Utilidades comunes para el sistema.
"""
from typing import List, Optional
from rich.console import Console
from rich.prompt import Prompt


class UIHelper:
    """Helper para operaciones de interfaz de usuario."""
    
    def __init__(self):
        self.console = Console()
    
    def select_from_list(self, items: List[str], title: str, 
                        allow_all: bool = False) -> Optional[str]:
        """Permite al usuario seleccionar de una lista de elementos."""
        if not items:
            self.console.print(f"[bold red]No hay {title.lower()} disponibles.[/bold red]")
            return None
        
        self.console.print(f"Seleccione {title.lower()}:", style="bold blue")
        
        for i, item in enumerate(items, 1):
            self.console.print(f"{i}. {item}", style="bold cyan")
        
        if allow_all:
            self.console.print(f"{len(items) + 1}. Todos", style="bold cyan")
        
        choice = Prompt.ask(
            f"Ingrese el número de {title.lower()} que desea seleccionar", 
            default="1", 
            show_default=True
        )
        
        try:
            choice_num = int(choice)
            
            if allow_all and choice_num == len(items) + 1:
                return "todos"
            
            if 1 <= choice_num <= len(items):
                return items[choice_num - 1]
            else:
                self.console.print(
                    f"[bold red]Selección no válida. Usando el primer {title.lower()} por defecto.[/bold red]"
                )
                return items[0]
                
        except ValueError:
            self.console.print(
                f"[bold red]Entrada no válida. Usando el primer {title.lower()} por defecto.[/bold red]"
            )
            return items[0]
    
    def get_hash_input(self) -> Optional[str]:
        """Obtiene un hash del usuario."""
        hash_value = Prompt.ask(
            "Por favor, ingresa el hash que deseas buscar (o escribe 'salir' para terminar)"
        )
        
        if hash_value.lower() == 'salir':
            self.console.print("[bold red]Saliendo...[/bold red]")
            return None
        
        return hash_value
    
    def display_welcome_message(self, app_name: str):
        """Muestra mensaje de bienvenida."""
        self.console.print(f"[bold green]¡Bienvenido a {app_name}![/bold green]")
    
    def display_success_message(self, message: str):
        """Muestra mensaje de éxito."""
        self.console.print(f"[bold green]{message}[/bold green]")
    
    def display_error_message(self, message: str):
        """Muestra mensaje de error."""
        self.console.print(f"[bold red]{message}[/bold red]")
    
    def display_info_message(self, message: str):
        """Muestra mensaje informativo."""
        self.console.print(f"[bold blue]{message}[/bold blue]")


class ValidationHelper:
    """Helper para validaciones."""
    
    @staticmethod
    def is_valid_hash(hash_value: str) -> bool:
        """Valida si el hash tiene un formato válido."""
        if not hash_value or not isinstance(hash_value, str):
            return False
        
        # Un hash típico debe tener al menos 8 caracteres y ser hexadecimal
        return len(hash_value) >= 8 and all(c in '0123456789ABCDEFabcdef' for c in hash_value)
    
    @staticmethod
    def is_valid_file_path(file_path: str) -> bool:
        """Valida si la ruta del archivo es válida."""
        try:
            from pathlib import Path
            return Path(file_path).exists()
        except Exception:
            return False
