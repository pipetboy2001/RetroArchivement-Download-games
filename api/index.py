from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
import webbrowser

app = Flask(__name__)
console = Console()
JSON_URL = "https://archive.org/download/retroachievements_collection_v5/TamperMonkeyRetroachievements.json"

# Descargar el archivo JSON desde la URL
def download_json(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"Error: {e}")
        return None

# Función para buscar por hash
def find_hash_in_json(json_data, hash_value):
    return next(
        (item[hash_value.upper()] for hash_list in json_data.values() for item in hash_list if hash_value.upper() in item),
        None
    )

# Función para obtener la URL de descarga
def get_download_url(rom_path: str) -> str:
    # Definir los prefix URLs para cada tipo de juego
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

    # Determinar el tipo de juego a partir del rom_path
    if "SNES-Super Famicom" in rom_path:
        return base_urls["SNES"] + rom_path.replace("\\", "/").replace(" ", "%20")
    elif "NES-Famicom" in rom_path:
        return base_urls["NES"] + rom_path.replace("\\", "/").replace(" ", "%20")
    elif "arcade" in rom_path:
        return base_urls["ARCADE"] + rom_path.replace("\\", "/").replace(" ", "%20").replace("arcade/", "")
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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']
    json_data = download_json(JSON_URL)
    if json_data:
        hash_value = find_hash_in_json(json_data, search_term)
        if hash_value:
            download_url = get_download_url(hash_value)
            return render_template('search_result.html', download_url=download_url)
        else:
            flash(f"No se encontró el hash '{search_term}' en el JSON.", 'error')
    else:
        flash("Error al descargar el JSON.", 'error')
    return redirect(url_for('index'))


@app.route('/open_browser', methods=['POST'])
def open_browser():
    download_url = request.form['download_url']
    webbrowser.open(download_url)
    return redirect(url_for('index'))



@app.route('/open_url', methods=['POST'])
def open_url():
    url = request.form['url']
    webbrowser.open(url)
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    console.print(Text("Error 404: Página no encontrada.", style="bold red"))
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    console.print(Text("Error 500: Error interno del servidor.", style="bold red"))
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)