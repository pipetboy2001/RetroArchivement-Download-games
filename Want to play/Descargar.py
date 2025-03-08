import json
import requests
import webbrowser
import sys
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

JSON_URL = './TamperMonkeyRetroachievements.json'
console = Console()

DOWNLOAD_MSG = "Descargando archivo JSON..."
HASH_FOUND_MSG = "Hash encontrado. La URL de descarga es: {}"
HASH_NOT_FOUND_MSG = "Hash [bold yellow]{}[/bold yellow] no encontrado en el archivo JSON."
ERROR_HTTP_MSG = "Error HTTP al descargar el archivo JSON: {}"
ERROR_MSG = "Error al descargar el archivo JSON: {}"

def download_json(url: str) -> Optional[Dict[str, Any]]:
    max_attempts = 5  
    attempt = 0      
    while attempt < max_attempts:
        attempt += 1
        try:
            console.print(f"Intento {attempt}/{max_attempts}: Descargando archivo JSON...")
            response = requests.get(url)
            response.raise_for_status()  # Lanza un error para códigos de estado 4xx o 5xx
            return response.json()  # Devolvemos el contenido como un objeto JSON
        except requests.exceptions.HTTPError as http_err:
            console.print(ERROR_HTTP_MSG.format(http_err), style="bold red")
        except Exception as err:
            console.print(ERROR_MSG.format(err), style="bold red")
        if attempt < max_attempts:
            continue_download = Prompt.ask("¿Deseas intentar nuevamente? (s/n)", default="s").lower()
            if continue_download != "s":
                console.print("[bold red]Descarga cancelada por el usuario.[/bold red]")
                return None
    console.print("[bold red]Se alcanzó el número máximo de intentos.[/bold red]")
    return None

def find_hash_in_json(json_data: Dict[str, Any], hash_value: str) -> Optional[str]:
    return next(
        (item[hash_value.upper()] for hash_list in json_data.values() for item in hash_list if hash_value.upper() in item),
        None
    )

def get_download_url(rom_path: str) -> str:
    base_urls = {
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
    elif "PlayStation Portable" in rom_path:
        game_folder = rom_path.split("/")[1] 
        game_file = rom_path.split("/")[-1]
        return base_urls["PSP"] + game_folder + "/" + game_file.replace(" ", "%20").replace("!", "%21").replace("(", "%28").replace(")", "%29")
    elif "PlayStation 2" in rom_path:
        # Para juegos de PS2, determinamos la letra inicial del juego
        game_folder = rom_path.split("/")[-2] 
        game_file = rom_path.split("/")[-1] 
        first_letter = game_folder[0].upper() 

        # Determinar la URL correcta según la letra inicial
        if 'A' <= first_letter <= 'M':
            return base_urls["PS2_A_M"] + game_folder + "/" + game_file.replace("\\", "/").replace(" ", "%20")
        elif 'N' <= first_letter <= 'Z':
            return base_urls["PS2_N_Z"] + game_folder + "/" + game_file.replace("\\", "/").replace(" ", "%20")
    elif "PlayStation" in rom_path:
        game_folder = rom_path.split("/")[-2] 
        game_file = rom_path.split("/")[-1] 
        return base_urls["PS1"] + game_folder + "/" + game_file.replace("\\", "/").replace(" ", "%20")
    else:  
        return base_urls["DC"] + rom_path.replace("\\", "/").replace(" ", "%20")

def open_url_in_browser(url: str) -> None:
    console.print(f"Abriendo [link]{url}[/link] en el navegador...", style="bold blue")
    webbrowser.open(url)

def main() -> None:
    # Verificar si el hash fue proporcionado como argumento
    if len(sys.argv) < 2:
        console.print("[bold red]Por favor, proporciona un hash como parámetro.[/bold red]")
        return

    hash_value = sys.argv[1]  # Obtener el hash del parámetro

    console.print(DOWNLOAD_MSG)
    with open(JSON_URL, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    if json_data:
        console.print(f"Buscando el hash [bold yellow]{hash_value}[/bold yellow] en el archivo JSON...")
        rom_path = find_hash_in_json(json_data, hash_value)

        if rom_path:
            download_url = get_download_url(rom_path)
            console.print(HASH_FOUND_MSG.format(download_url), style="bold green")
            open_url_in_browser(download_url)
        else:
            console.print(HASH_NOT_FOUND_MSG.format(hash_value), style="bold red")
            sys.exit(1)
    else:
        console.print("No se pudo descargar o procesar el archivo JSON.", style="bold red")
        
if __name__ == "__main__":
    main()
