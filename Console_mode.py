import json
from rich.console import Console
from rich.prompt import Prompt
import webbrowser
from typing import Optional, Dict, Any
# Inicializar consola de Rich
console = Console()

# Ruta al archivo JSON local
JSON_FILE_PATH = "Data/TamperMonkeyRetroachievements.json"

# Mensajes constantes
HASH_FOUND_MSG = "Hash encontrado. La URL de descarga es: {}"
HASH_NOT_FOUND_MSG = "Hash [bold yellow]{}[/bold yellow] no encontrado en el archivo JSON."
ERROR_MSG = "Error al cargar el archivo JSON: {}"

# Función para cargar el archivo JSON local
def load_local_json(file_path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        console.print(f"[bold red]Archivo JSON no encontrado: {file_path}[/bold red]")
        return None
    except json.JSONDecodeError as e:
        console.print(f"[bold red]Error al decodificar el archivo JSON: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]{ERROR_MSG.format(e)}[/bold red]")
        return None

# Función para buscar el hash en el archivo JSON
def find_hash_in_json(json_data: Dict[str, Any], hash_value: str) -> Optional[str]:
    hash_upper = hash_value.upper()
    for console_id, hash_list in json_data.items():
        for item in hash_list:
            if hash_upper in item:
                return item[hash_upper]
    return None

# Función para obtener la URL de descarga correcta
def get_download_url(rom_path: str) -> str:
    base_urls = {
        "ARCADE": "https://archive.org/download/fbnarcade-fullnonmerged/arcade/",
        "SNES": "https://archive.org/download/retroachievements_collection_SNES-Super_Famicom/",
        "NES": "https://archive.org/download/retroachievements_collection_NES-Famicom/",
        "PSP": "https://dn720005.ca.archive.org/0/items/retroachievements_collection_PlayStation_Portable/PlayStation%20Portable/",
        "PS1": "https://archive.org/download/retroachievements_collection_PlayStation/PlayStation/",
        "PS2_A_M": "https://archive.org/download/retroachievements_collection_PlayStation_2_A-M/PlayStation%202/",
        "PS2_N_Z": "https://archive.org/download/retroachievements_collection_PlayStation_2_N-Z/PlayStation%202/",
        "DC": "https://archive.org/download/retroachievements_collection_v5/"
    }

    if "SNES-Super Famicom" in rom_path:
        return base_urls["SNES"] + rom_path.replace("\\", "/").replace(" ", "%20")
    elif "NES-Famicom" in rom_path:
        return base_urls["NES"] + rom_path.replace("\\", "/").replace(" ", "%20")
    elif "Genesis-Mega Drive" in rom_path or "Sega CD" in rom_path:
        return base_urls["DC"] + rom_path.replace("\\", "/").replace(" ", "%20")
    elif "PlayStation Portable" in rom_path:
        return base_urls["PSP"] + rom_path.replace("\\", "/").replace(" ", "%20")
    elif "PlayStation 2" in rom_path:
        # Decidir entre A-M o N-Z basado en el nombre del juego
        game_name = rom_path.split('/')[-1] if '/' in rom_path else rom_path
        if game_name and game_name[0].upper() < 'N':
            return base_urls["PS2_A_M"] + rom_path.replace("\\", "/").replace(" ", "%20")
        else:
            return base_urls["PS2_N_Z"] + rom_path.replace("\\", "/").replace(" ", "%20")
    elif "PlayStation" in rom_path:
        return base_urls["PS1"] + rom_path.replace("\\", "/").replace(" ", "%20")
    elif "Arcade" in rom_path:
        return base_urls["ARCADE"] + rom_path.replace("\\", "/").replace(" ", "%20")
    else:
        # URL por defecto
        return base_urls["DC"] + rom_path.replace("\\", "/").replace(" ", "%20")

# Función para abrir la URL en el navegador
def open_url_in_browser(url: str) -> None:
    console.print(f"Abriendo [link]{url}[/link] en el navegador...", style="bold blue")
    webbrowser.open(url)

# Función principal
def main():
    console.print("[bold green]Bienvenido al buscador de juegos de RetroAchievements![/bold green]")
    
    # Cargar el archivo JSON local
    json_data = load_local_json(JSON_FILE_PATH)

    if json_data:
        console.print("[bold green]Archivo JSON cargado con éxito.[/bold green]")
        
        while True:
            hash_value = Prompt.ask("Por favor, ingresa el hash que deseas buscar (o escribe 'salir' para terminar)")

            if hash_value.lower() == 'salir':
                console.print("[bold red]Saliendo...[/bold red]")
                break

            # Buscar el hash en el archivo JSON
            rom_path = find_hash_in_json(json_data, hash_value)

            if rom_path:
                # Si el hash se encuentra, obtenemos la URL de descarga
                download_url = get_download_url(rom_path)
                if download_url:
                    console.print(HASH_FOUND_MSG.format(download_url), style="bold green")
                    open_url_in_browser(download_url)
                else:
                    console.print("[bold red]No se pudo generar la URL de descarga.[/bold red]")
            else:
                console.print(HASH_NOT_FOUND_MSG.format(hash_value), style="bold red")
    else:
        console.print("[bold red]No se pudo cargar el archivo JSON local.[/bold red]")

# Ejecutar el programa
if __name__ == "__main__":
    main()
