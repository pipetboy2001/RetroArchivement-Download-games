from flask import Flask, render_template, request, redirect, url_for, flash
import json
import webbrowser
import time
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para usar flash

# Ruta al archivo JSON local
JSON_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'TamperMonkeyRetroachievements.json')

cached_json_data = None

# Cargar el archivo JSON local
def load_json_file():
    global cached_json_data
    if cached_json_data is None:
        try:
            print(f"Cargando JSON desde {JSON_FILE_PATH}...")
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
                cached_json_data = json.load(file)
            print("JSON cargado exitosamente.")
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo JSON en {JSON_FILE_PATH}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error al decodificar el JSON: {e}")
            return None
        except Exception as e:
            print(f"Error al cargar el JSON: {e}")
            return None
    return cached_json_data

# Función para contar total de juegos en la base de datos (optimizada)
def count_total_games(json_data):
    # Simplemente contar el número de IDs únicos de juegos
    return len(json_data) if json_data else 0

# Función para extraer el nombre del juego de la ruta
def extract_game_name(rom_path):
    # Extraer el nombre del juego de la ruta del ROM
    parts = rom_path.split('/')
    if len(parts) >= 2:
        return parts[1]  # El nombre del juego está en la segunda posición
    return rom_path

# Función para extraer información detallada de un ROM
def analyze_rom_info(rom_path):
    parts = rom_path.split('/')
    filename = parts[-1] if parts else rom_path
    
    # Determinar tipo de ROM
    is_hack = "[Hack]" in filename
    is_translation = "[T+" in filename
    is_original = "[!]" in filename
    
    # Extraer región
    region = "Unknown"
    if "(U)" in filename:
        region = "USA"
    elif "(E)" in filename:
        region = "Europe"
    elif "(J)" in filename:
        region = "Japan"
    elif "(UE)" in filename:
        region = "USA/Europe"
    
    # Determinar prioridad (menor número = mayor prioridad)
    priority = 0
    if is_original and not is_hack and not is_translation:
        priority = 1  # ROMs originales tienen máxima prioridad
    elif is_original and is_translation:
        priority = 2  # Traducciones oficiales
    elif is_hack:
        priority = 3  # Hacks tienen menor prioridad
    else:
        priority = 4  # Otros
    
    return {
        'filename': filename,
        'region': region,
        'is_hack': is_hack,
        'is_translation': is_translation,
        'is_original': is_original,
        'priority': priority
    }

# Función para buscar juegos por nombre (mejorada con múltiples versiones)
def search_games_by_name(json_data, search_term):
    search_term = search_term.lower()
    matching_games = []
    
    for game_id, hash_list in json_data.items():
        if len(matching_games) >= 10:  # Limitar a 10 juegos diferentes
            break
            
        for item in hash_list:
            versions = []
            game_name = None
            
            for hash_key, rom_path in item.items():
                current_game_name = extract_game_name(rom_path)
                if not game_name:
                    game_name = current_game_name
                
                if search_term in current_game_name.lower():
                    rom_info = analyze_rom_info(rom_path)
                    versions.append({
                        'hash': hash_key,
                        'rom_path': rom_path,
                        'info': rom_info
                    })
            
            if versions and game_name:
                # Ordenar versiones por prioridad
                versions.sort(key=lambda x: x['info']['priority'])
                
                matching_games.append({
                    'id': game_id,
                    'name': game_name,
                    'versions': versions,
                    'primary_version': versions[0],  # La versión de mayor prioridad
                    'total_versions': len(versions)
                })
                break  # Solo tomar el primer resultado por juego
        
    return matching_games[:10]  # Asegurar que no se excedan 10 resultados

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
    json_data = load_json_file()
    total_games = count_total_games(json_data) if json_data else 0
    return render_template('index.html', total_games=total_games)

@app.route('/get_game_versions', methods=['POST'])
def get_game_versions():
    game_id = request.form.get('game_id', '')
    json_data = load_json_file()
    
    if json_data and game_id in json_data:
        versions = []
        for item in json_data[game_id]:
            for hash_key, rom_path in item.items():
                rom_info = analyze_rom_info(rom_path)
                versions.append({
                    'hash': hash_key,
                    'rom_path': rom_path,
                    'info': rom_info
                })
        
        # Ordenar por prioridad
        versions.sort(key=lambda x: x['info']['priority'])
        
        return {'success': True, 'versions': versions}
    else:
        return {'success': False, 'versions': []}

@app.route('/search_games', methods=['POST'])
def search_games():
    search_term = request.form.get('search_term', '')
    json_data = load_json_file()
    
    if json_data and search_term:
        matching_games = search_games_by_name(json_data, search_term)
        # Simplificar para el frontend
        simplified_games = []
        for game in matching_games:
            simplified_games.append({
                'id': game['id'],
                'name': game['name'],
                'hash': game['primary_version']['hash'],
                'rom_path': game['primary_version']['rom_path'],
                'total_versions': game['total_versions'],
                'primary_info': game['primary_version']['info']
            })
        return {'success': True, 'games': simplified_games}
    else:
        return {'success': False, 'games': []}

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']
    json_data = load_json_file()
    
    if json_data:
        hash_value = find_hash_in_json(json_data, search_term)
        if hash_value:
            download_url = get_download_url(hash_value)
            return {'success': True, 'download_url': download_url}  # Devuelve URL si se encuentra el hash
        else:
            return {'success': False, 'message': f"No se encontró el hash '{search_term}' en la base de datos."}, 404
    else:
        return {'success': False, 'message': "Error al cargar el archivo JSON local."}, 500


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
