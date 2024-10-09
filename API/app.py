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
        game_folder = rom_path.split("/")[1]
        game_file = rom_path.split("/")[-1]
        return base_urls["PSP"] + game_folder + "/" + game_file.replace(" ", "%20").replace("!", "%21").replace("(", "%28").replace(")", "%29")
    elif "PlayStation 2" in rom_path:
        game_folder = rom_path.split("/")[-2]
        game_file = rom_path.split("/")[-1]
        first_letter = game_folder[0].upper()
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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    hash_value = request.form['hash']
    json_data = download_json(JSON_URL)

    if json_data:
        rom_path = find_hash_in_json(json_data, hash_value)
        if rom_path:
            download_url = get_download_url(rom_path)
            flash(f'Hash encontrado. La URL de descarga es: {download_url}', 'success')
            return redirect(download_url)
        else:
            flash(f'Hash {hash_value} no encontrado.', 'danger')
            return redirect(url_for('index'))
    else:
        flash('Error al descargar el archivo JSON.', 'danger')
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
