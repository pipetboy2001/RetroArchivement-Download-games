import json
import requests
import webbrowser
import sys
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

# URL del archivo JSON que contiene los hashes
JSON_URL = "https://archive.org/download/retroachievements_collection_v5/TamperMonkeyRetroachievements.json"

# Inicializar consola de Rich
console = Console()

# Mensajes constantes
DOWNLOAD_MSG = "Descargando archivo JSON..."
HASH_FOUND_MSG = "Hash encontrado. La URL de descarga es: {}"
HASH_NOT_FOUND_MSG = "Hash [bold yellow]{}[/bold yellow] no encontrado en el archivo JSON."
ERROR_HTTP_MSG = "Error HTTP al descargar el archivo JSON: {}"
ERROR_MSG = "Error al descargar el archivo JSON: {}"

# Función para descargar el archivo JSON desde archive.org
def download_json(url: str) -> Optional[Dict[str, Any]]:
    max_attempts = 5  # Máximo de intentos
    attempt = 0       # Contador de intentos

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

        # Preguntar al usuario si desea continuar con el siguiente intento
        if attempt < max_attempts:
            continue_download = Prompt.ask("¿Deseas intentar nuevamente? (s/n)", default="s").lower()
            if continue_download != "s":
                console.print("[bold red]Descarga cancelada por el usuario.[/bold red]")
                return None

    console.print("[bold red]Se alcanzó el número máximo de intentos.[/bold red]")
    return None


# Función para buscar el hash en el archivo JSON
def find_hash_in_json(json_data: Dict[str, Any], hash_value: str) -> Optional[str]:
    return next(
        (item[hash_value.upper()] for hash_list in json_data.values() for item in hash_list if hash_value.upper() in item),
        None
    )

# Función para obtener la URL de descarga correcta
def get_download_url(rom_path: str) -> str:
    # Definir los prefix URLs para cada tipo de juego
    base_urls = {
        "SNES": "https://archive.org/download/retroachievements_collection_SNES-Super_Famicom/",
        "NES": "https://archive.org/download/retroachievements_collection_NES-Famicom/",
        "PSP": "https://dn720005.ca.archive.org/0/items/retroachievements_collection_PlayStation_Portable/PlayStation%20Portable/",
        "PS1": "https://archive.org/download/retroachievements_collection_PlayStation/PlayStation/",
        "PS2_A_M": "https://archive.org/download/retroachievements_collection_PlayStation_2_A-M/PlayStation%202/",
        "PS2_N_Z": "https://archive.org/download/retroachievements_collection_PlayStation_2_N-Z/PlayStation%202/",
        "DC": "https://archive.org/download/retroachievements_collection_v5/"
    }

    # Determinar el tipo de juego a partir del rom_path
    if "SNES-Super Famicom" in rom_path:
        return base_urls["SNES"] + rom_path.replace("\\", "/").replace(" ", "%20")
    elif "NES-Famicom" in rom_path:
        return base_urls["NES"] + rom_path.replace("\\", "/").replace(" ", "%20")
    elif "PlayStation Portable" in rom_path:
        # Descomponemos el rom_path para extraer el nombre del juego
        game_folder = rom_path.split("/")[1]  # Carpeta del juego
        game_file = rom_path.split("/")[-1]  # Nombre del archivo
        return base_urls["PSP"] + game_folder + "/" + game_file.replace(" ", "%20").replace("!", "%21").replace("(", "%28").replace(")", "%29")
    elif "PlayStation 2" in rom_path:
        # Para juegos de PS2, determinamos la letra inicial del juego
        game_folder = rom_path.split("/")[-2]  # Carpeta del juego
        game_file = rom_path.split("/")[-1]  # Nombre del archivo
        first_letter = game_folder[0].upper()  # Obtener la primera letra del juego

        # Determinar la URL correcta según la letra inicial
        if 'A' <= first_letter <= 'M':
            return base_urls["PS2_A_M"] + game_folder + "/" + game_file.replace("\\", "/").replace(" ", "%20")
        elif 'N' <= first_letter <= 'Z':
            return base_urls["PS2_N_Z"] + game_folder + "/" + game_file.replace("\\", "/").replace(" ", "%20")
    elif "PlayStation" in rom_path:
        # Descomponemos el rom_path para extraer el nombre del juego
        game_folder = rom_path.split("/")[-2]  # Carpeta del juego
        game_file = rom_path.split("/")[-1]  # Nombre del archivo
        return base_urls["PS1"] + game_folder + "/" + game_file.replace("\\", "/").replace(" ", "%20")
    else:  # Para Dreamcast u otros
        return base_urls["DC"] + rom_path.replace("\\", "/").replace(" ", "%20")

# Función para abrir la URL en el navegador
def open_url_in_browser(url: str) -> None:
    console.print(f"Abriendo [link]{url}[/link] en el navegador...", style="bold blue")
    webbrowser.open(url)

# Función principal
def main() -> None:
    # Verificar si el hash fue proporcionado como argumento
    if len(sys.argv) < 2:
        console.print("[bold red]Por favor, proporciona un hash como parámetro.[/bold red]")
        return

    hash_value = sys.argv[1]  # Obtener el hash del parámetro

    # Descargar el archivo JSON una vez
    console.print(DOWNLOAD_MSG)
    json_data = download_json(JSON_URL)

    if json_data:
        # Buscar el hash en el archivo JSON
        console.print(f"Buscando el hash [bold yellow]{hash_value}[/bold yellow] en el archivo JSON...")
        rom_path = find_hash_in_json(json_data, hash_value)

        if rom_path:
            # Si el hash se encuentra, obtenemos la URL de descarga
            download_url = get_download_url(rom_path)
            console.print(HASH_FOUND_MSG.format(download_url), style="bold green")
            open_url_in_browser(download_url)
        else:
            console.print(HASH_NOT_FOUND_MSG.format(hash_value), style="bold red")
            # Añadir un valor de retorno para indicar que el hash no se encontró
            sys.exit(1)

            
    else:
        console.print("No se pudo descargar o procesar el archivo JSON.", style="bold red")

# Ejecutar el programa
if __name__ == "__main__":
    main()
