from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import webbrowser
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para usar flash
JSON_URL = "https://archive.org/download/retroachievements_collection_v5/TamperMonkeyRetroachievements.json"

cached_json_data = None

# Descargar el archivo JSON desde la URL
def download_json(url: str):
    global cached_json_data
    if cached_json_data is None:
        try:
            print(f"Descargando JSON desde {url}...")
            response = requests.get(url)
            response.raise_for_status()
            cached_json_data = response.json()
            print("JSON descargado exitosamente.")
        except requests.exceptions.RequestException as e:
            print(f"Error al descargar el JSON: {e}")
            return None
    return cached_json_data

# Función para buscar por hash
def find_hash_in_json(json_data, hash_value):
    hash_value = hash_value.upper()
    print(f"Buscando hash: {hash_value}")  # Log de búsqueda
    for hash_list in json_data.values():
        for item in hash_list:
            if hash_value in item:
                print(f"Hash encontrado: {item[hash_value]}")  # Log si se encuentra el hash
                return item[hash_value]
    print("Hash no encontrado.")  # Log si no se encuentra
    return None

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
    print(f"Obteniendo URL de descarga para: {rom_path}")  # Log de descarga
    if "SNES-Super Famicom" in rom_path:
        return base_urls["SNES"] + rom_path.replace("\\", "/").replace(" ", "%20")
    elif "NES-Famicom" in rom_path:
        return base_urls["NES"] + rom_path.replace("\\", "/").replace(" ", "%20")
    elif "arcade" in rom_path:
        return base_urls["ARCADE"] + rom_path.replace("\\", "/").replace(" ", "%20").replace("arcade/", "")
    elif "PlayStation Portable" in rom_path:
        game_folder, game_file = rom_path.split("/")[1], rom_path.split("/")[-1]
        return base_urls["PSP"] + game_folder + "/" + game_file.replace(" ", "%20").replace("!", "%21").replace("(", "%28").replace(")", "%29")
    elif "PlayStation 2" in rom_path:
        game_folder, game_file = rom_path.split("/")[-2], rom_path.split("/")[-1]
        first_letter = game_folder[0].upper()
        if 'A' <= first_letter <= 'M':
            return base_urls["PS2_A_M"] + game_folder + "/" + game_file.replace("\\", "/").replace(" ", "%20")
        elif 'N' <= first_letter <= 'Z':
            return base_urls["PS2_N_Z"] + game_folder + "/" + game_file.replace("\\", "/").replace(" ", "%20")
    elif "PlayStation" in rom_path:
        game_folder, game_file = rom_path.split("/")[-2], rom_path.split("/")[-1]
        return base_urls["PS1"] + game_folder + "/" + game_file.replace("\\", "/").replace(" ", "%20")
    else:
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
            return {'success': True, 'download_url': download_url}  # Devuelve URL si se encuentra el hash
        else:
            return {'success': False, 'message': f"No se encontró el hash '{search_term}' en la base de datos."}, 404
    else:
        return {'success': False, 'message': "Error al descargar el JSON desde la URL."}, 500


@app.route('/open_browser', methods=['POST'])
def open_browser(download_url):
    print(f"Abrir el navegador con la URL: {download_url}")  # Log de apertura
    webbrowser.open(download_url)
    flash("El juego se está descargando...", 'success')  # Mensaje de éxito al abrir el navegador
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
