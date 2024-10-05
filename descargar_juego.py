import json
import requests
import webbrowser
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

# URL del archivo JSON que contiene los hashes
JSON_URL = "https://archive.org/download/retroachievements_collection_v5/TamperMonkeyRetroachievements.json"

# Inicializar consola de Rich
console = Console()

ascii_art = r"""

             _                             _      _                                            _        
            | |                           | |    (_)                                          | |       
  _ __  ___ | |_  _ __  ___    __ _   ___ | |__   _   ___ __   __ ___  _ __ ___    ___  _ __  | |_  ___ 
 | '__|/ _ \| __|| '__|/ _ \  / _` | / __|| '_ \ | | / _ \\ \ / // _ \| '_ ` _ \  / _ \| '_ \ | __|/ __|
 | |  |  __/| |_ | |  | (_) || (_| || (__ | | | || ||  __/ \ V /|  __/| | | | | ||  __/| | | || |_ \__ \
 |_|   \___| \__||_|   \___/  \__,_| \___||_| |_||_| \___|  \_/  \___||_| |_| |_| \___||_| |_| \__||___/
                                                                                                        
                                                                                                        

"""

# Mensajes constantes
DOWNLOAD_MSG = "Descargando archivo JSON..."
HASH_FOUND_MSG = "Hash encontrado. La URL de descarga es: {}"
HASH_NOT_FOUND_MSG = "Hash [bold yellow]{}[/bold yellow] no encontrado en el archivo JSON."
ERROR_HTTP_MSG = "Error HTTP al descargar el archivo JSON: {}"
ERROR_MSG = "Error al descargar el archivo JSON: {}"

# Función para descargar el archivo JSON desde archive.org
def download_json(url: str) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error para códigos de estado 4xx o 5xx
        return response.json()  # Devolvemos el contenido como un objeto JSON
    except requests.exceptions.HTTPError as http_err:
        console.print(ERROR_HTTP_MSG.format(http_err), style="bold red")
    except Exception as err:
        console.print(ERROR_MSG.format(err), style="bold red")
    return None

# Función para buscar el hash en el archivo JSON
def find_hash_in_json(json_data: Dict[str, Any], hash_value: str) -> Optional[str]:
    return next(
        (item[hash_value.upper()] for hash_list in json_data.values() for item in hash_list if hash_value.upper() in item),
        None
    )

# Función para abrir la URL en el navegador
def open_url_in_browser(url: str) -> None:
    console.print(f"Abriendo [link]{url}[/link] en el navegador...", style="bold blue")
    webbrowser.open(url)

# Función principal
def main() -> None:
    console.print(ascii_art)  # Imprimir arte ASCII
    console.print("[bold green]Bienvenido al buscador de juegos de RetroArchivements![/bold green]")
    
    # Descargar el archivo JSON una vez
    console.print(DOWNLOAD_MSG)
    json_data = download_json(JSON_URL)

    if json_data:
        while True:
            # Solicitar al usuario que ingrese un hash
            hash_value = Prompt.ask("Por favor, ingresa el hash que deseas buscar (o escribe 'salir' para terminar)")
            
            if hash_value.lower() == 'salir':
                console.print("[bold red]Saliendo...[/bold red]")
                break

            # Buscar el hash en el archivo JSON
            console.print(f"Buscando el hash [bold yellow]{hash_value}[/bold yellow] en el archivo JSON...")
            rom_path = find_hash_in_json(json_data, hash_value)

            if rom_path:
                # Si el hash se encuentra, abrimos la URL de descarga en el navegador
                base_url = "https://archive.org/download/retroachievements_collection_v5/"
                download_url = base_url + rom_path.replace("\\", "/").replace(" ", "%20")
                console.print(HASH_FOUND_MSG.format(download_url), style="bold green")
                open_url_in_browser(download_url)
            else:
                console.print(HASH_NOT_FOUND_MSG.format(hash_value), style="bold red")
    else:
        console.print("No se pudo descargar o procesar el archivo JSON.", style="bold red")

# Ejecutar el programa
if __name__ == "__main__":
    main()
