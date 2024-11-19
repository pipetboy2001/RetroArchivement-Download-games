import requests
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
import webbrowser
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Inicializar consola de Rich
console = Console()
# URLs
LOGIN_URL = "https://archive.org/account/login"
JSON_URL = "https://archive.org/download/retroachievements_collection_v5/TamperMonkeyRetroachievements.json"


load_dotenv()  # Esto carga las variables del .env en las variables de entorno
# Obtener credenciales del usuario del .env
USERNAME = os.getenv("ARCHIVE_USERNAME")
PASSWORD = os.getenv("ARCHIVE_PASSWORD")

# Mensajes constantes
DOWNLOAD_MSG = "Descargando archivo JSON..."
HASH_FOUND_MSG = "Hash encontrado. La URL de descarga es: {}"
HASH_NOT_FOUND_MSG = "Hash [bold yellow]{}[/bold yellow] no encontrado en el archivo JSON."
ERROR_HTTP_MSG = "Error HTTP al descargar el archivo JSON: {}"
ERROR_MSG = "Error al descargar el archivo JSON: {}"

# Función para iniciar sesión en Archive.org
def login_to_archive(username: str, password: str) -> Optional[requests.Session]:
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}

    try:
        # Obtener la página de login para extraer cookies y tokens
        login_page = session.get(LOGIN_URL, headers=headers)
        login_page.raise_for_status()
        
        # Extraer el token CSRF
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find("input", {"name": "csrf"})['value'] if soup.find("input", {"name": "csrf"}) else None

        # Datos del formulario de inicio de sesión
        payload = {
            'username': username,
            'password': password,
            'submit': 'Log In'
        }
        
        # Si hay un token CSRF, agregarlo al payload
        if csrf_token:
            payload['csrf'] = csrf_token
        
        # Enviar la petición POST para autenticar al usuario
        response = session.post(LOGIN_URL, data=payload, headers=headers, allow_redirects=True)
        response.raise_for_status()

        # Verificar si la autenticación fue exitosa
        login_response = response.json()
        if login_response.get("status") == "ok" and login_response.get("message") == "Successful login.":
            console.print("[bold green]Autenticación exitosa.[/bold green]")
            return session
        else:
            console.print("[bold red]Error de autenticación. Verifica tus credenciales.[/bold red]")
            return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error durante la autenticación: {e}[/bold red]")
        return None
    except ValueError as e:
        console.print(f"[bold red]Error al procesar la respuesta JSON: {e}[/bold red]")
        return None

# Función para descargar el archivo JSON autenticado
def download_json_with_auth(session: requests.Session, url: str) -> Optional[Dict[str, Any]]:
    try:
        response = session.get(url)
        response.raise_for_status()  # Lanza un error para códigos de estado 4xx o 5xx
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        console.print(f"[bold red]{ERROR_HTTP_MSG.format(http_err)}[/bold red]")
    except Exception as err:
        console.print(f"[bold red]{ERROR_MSG.format(err)}[/bold red]")

    return None

# Función para descargar el archivo JSON con reintentos
def download_json(url: str) -> Optional[Dict[str, Any]]:
    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        console.print(f"Intento {attempt}/{max_attempts}: {DOWNLOAD_MSG}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
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
    # Agregar más casos para otros tipos de juego...

# Función para abrir la URL en el navegador
def open_url_in_browser(url: str) -> None:
    console.print(f"Abriendo [link]{url}[/link] en el navegador...", style="bold blue")
    webbrowser.open(url)

# Función principal
def main():
    # Iniciar sesión con las credenciales almacenadas en las variables
    session = login_to_archive(USERNAME, PASSWORD)
    
    if session:
        console.print("[bold green]Bienvenido al buscador de juegos de RetroAchievements![/bold green]")
        # Descargar el archivo JSON usando la sesión autenticada
        json_data = download_json_with_auth(session, JSON_URL)

        if json_data:
            console.print("[bold green]Archivo JSON descargado con éxito.[/bold green]")
            # Aquí continuarías con la lógica de búsqueda de hashes y demás
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
                    console.print(HASH_FOUND_MSG.format(download_url), style="bold green")
                    open_url_in_browser(download_url)
                else:
                    console.print(HASH_NOT_FOUND_MSG.format(hash_value), style="bold red")
        else:
            console.print("[bold red]No se pudo descargar el archivo JSON.[/bold red]")
    else:
        console.print("[bold red]No se pudo iniciar sesión.[/bold red]")

# Ejecutar el programa
if __name__ == "__main__":
    main()
