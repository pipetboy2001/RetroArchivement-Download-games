from flask import Flask, render_template, request, redirect, url_for, flash
import json
import webbrowser
import time
import os
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para usar flash

# Ruta al archivo JSON local
JSON_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'TamperMonkeyRetroachievements.json')

cached_json_data = None
cached_games_index = None  # Índice cacheado para listados

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
    # Extraer nombre del juego usando la carpeta inmediatamente anterior al archivo;
    # si no es válida (p.ej. !_flycast o consola raíz), usar el nombre del archivo sin extensión.
    path = rom_path.replace('\\', '/').strip()
    parts = [p for p in path.split('/') if p]
    if not parts:
        return rom_path
    filename = parts[-1]
    root = parts[0]
    folder = parts[-2] if len(parts) >= 2 else ''

    def clean(name: str) -> str:
        # Quitar extensión y normalizar espacios/guiones bajos
        base = name.rsplit('.', 1)[0]
        base = base.replace('_', ' ').strip()
        # Compactar múltiples espacios
        return ' '.join(base.split())

    invalid_folder_names = {root.lower(), 'arcade'}
    is_invalid = (not folder) or folder.lower() in invalid_folder_names or folder.startswith('!_')
    candidate = folder if not is_invalid else clean(filename)
    return candidate

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

# Deducir consola a partir de la carpeta raíz del rom_path
def get_console_from_rom_path(rom_path: str) -> str:
    """Devuelve el nombre canónico de consola a partir de la carpeta raíz.
    Unifica alias, abreviaturas y variaciones (p.ej. nes/NES, megadriv -> Genesis/Mega Drive, npg -> Neo Geo Pocket).
    """
    norm = rom_path.replace('\\', '/').strip()
    root = norm.split('/', 1)[0] if '/' in norm else norm
    raw = root.strip()

    # Normalización básica del texto del root
    t = raw.lower()
    for ch in ['_', '-', '&', '(', ')', '[', ']', ',', '.']:
        t = t.replace(ch, ' ')
    t = ' '.join(t.split())  # compactar espacios

    # Mapa de alias -> nombre canónico
    aliases = {
        # Arcade
        'arcade': 'ARCADE',

        # Nintendo
        'snes': 'SNES',
        'snes super famicom': 'SNES',
        'super nintendo': 'SNES',
        'nes': 'NES',
        'nes famicom': 'NES',
        'nintendo 64': 'N64',
        'n64': 'N64',
        'nintendo ds': 'Nintendo DS',
        'nds': 'Nintendo DS',
        'game boy': 'Game Boy',
        'gb': 'Game Boy',
        'game boy color': 'Game Boy Color',
        'gbc': 'Game Boy Color',
        'game boy advance': 'Game Boy Advance',
        'gba': 'Game Boy Advance',

        # Sega
        'genesis': 'Genesis/Mega Drive',
        'mega drive': 'Genesis/Mega Drive',
        'megadrive': 'Genesis/Mega Drive',
        'megadriv': 'Genesis/Mega Drive',
        'md': 'Genesis/Mega Drive',
        'genesis mega drive': 'Genesis/Mega Drive',
        'mega drive genesis': 'Genesis/Mega Drive',
        'sega master system': 'Master System',
        'master system': 'Master System',
        'sms': 'Master System',
        'game gear': 'Game Gear',
        'gg': 'Game Gear',
        'sega cd': 'Sega CD',
        'sega 32x': 'Sega 32X',
        '32x': 'Sega 32X',
        'dreamcast': 'Dreamcast',
        'dc': 'Dreamcast',

        # PlayStation
        'playstation': 'PS1',
        'psx': 'PS1',
        'ps1': 'PS1',
        'playstation 2': 'PS2',
        'ps2': 'PS2',
        'playstation portable': 'PSP',
        'psp': 'PSP',

        # NEC / PC Engine family
        'pc engine': 'PC Engine',
        'pcengine': 'PC Engine',
        'pce': 'PC Engine',
        'turbo grafx 16': 'TurboGrafx-16',
        'turbografx 16': 'TurboGrafx-16',
        'tg16': 'TurboGrafx-16',
        'supergrafx': 'SuperGrafx',
        'super grafx': 'SuperGrafx',

        # SNK Neo Geo Pocket
        'neo geo pocket': 'Neo Geo Pocket',
    'npg': 'Neo Geo Pocket',  # posible typo invertido
    'ngp': 'Neo Geo Pocket',
        'neo geo pocket color': 'Neo Geo Pocket Color',
        'ngpc': 'Neo Geo Pocket Color',

        # Atari
        'atari 2600': 'Atari 2600',
        'atari 7800': 'Atari 7800',
        'atari lynx': 'Atari Lynx',
        'atari jaguar': 'Atari Jaguar',

        # MSX
        'msx': 'MSX',
        'msx2': 'MSX2',

        # WonderSwan
        'wonderswan': 'WonderSwan',
        'ws': 'WonderSwan',
        'wonderswan color': 'WonderSwan Color',
        'wsc': 'WonderSwan Color',

        # Otros
        '3do': '3DO',
        'amiga': 'Amiga',
        'amiga cd32': 'Amiga CD32',
    # Sega SG-1000
    'sg 1000': 'SG-1000',
    'sg1000': 'SG-1000',
    'sg': 'SG-1000',  # solo si raíz es exactamente "sg", poco probable pero inofensivo
    'sega 1000': 'SG-1000',
    'sega1000': 'SG-1000',
    }

    # Devolver mapeo canónico si existe, si no, devolver la raíz original "bonita"
    if t in aliases:
        return aliases[t]

    # Como fallback, capitalizar palabras (evita duplicados por mayúsculas/minúsculas)
    pretty = ' '.join(w.capitalize() for w in t.split()) if t else raw
    return pretty or raw

# Construir índice de juegos para listados/filtrado
def build_games_index():
    global cached_games_index
    if cached_games_index is not None:
        return cached_games_index
    data = load_json_file()
    if not data:
        cached_games_index = []
        return cached_games_index
    games = []
    for game_id, hash_list in data.items():
        game_name = None
        consoles = set()
        total_versions = 0
        sample_rom_path = None
        for item in hash_list:
            for _hash, rom_path in item.items():
                if sample_rom_path is None:
                    sample_rom_path = rom_path
                total_versions += 1
                current_name = extract_game_name(rom_path)
                if not game_name:
                    game_name = current_name
                consoles.add(get_console_from_rom_path(rom_path))
        games.append({
            'id': game_id,
            'name': game_name or f'Game {game_id}',
            'consoles': sorted(list(consoles)),
            'versions': total_versions,
            'sample_rom_path': sample_rom_path
        })
    games.sort(key=lambda g: (g['name'] or '').lower())
    cached_games_index = games
    return cached_games_index

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
    # Helpers locales (alineados con src/factories/url_factory.py)
    def _normalize_slashes(path: str) -> str:
        return path.replace("\\", "/").lstrip("/")

    def _encode_rel_path(path: str) -> str:
        return quote(path, safe="/-_.")

    def _strip_first_segment_if_matches(path: str, segment: str) -> str:
        norm = _normalize_slashes(path)
        if norm.lower().startswith(segment.lower() + "/"):
            return norm.split("/", 1)[1]
        return norm

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
    norm = _normalize_slashes(rom_path)

    if "SNES-Super Famicom" in norm:
        return base_urls["SNES"] + _encode_rel_path(norm)
    elif "NES-Famicom" in norm:
        return base_urls["NES"] + _encode_rel_path(norm)
    # Arcade: si el primer segmento es 'arcade', quitarlo
    elif (norm.split("/", 1)[0].lower() == "arcade"):
        rel = norm.split("/", 1)[1] if "/" in norm else ""
        return base_urls["ARCADE"] + _encode_rel_path(rel)
    elif "playstation portable" in norm.lower():
        rel = _strip_first_segment_if_matches(norm, "PlayStation Portable")
        return base_urls["PSP"] + _encode_rel_path(rel)
    elif "playstation 2" in norm.lower():
        rel = _strip_first_segment_if_matches(norm, "PlayStation 2")
        game_name = rel.split('/')[-1] if '/' in rel else rel
        base = base_urls["PS2_A_M"] if (game_name and game_name[0].upper() < 'N') else base_urls["PS2_N_Z"]
        return base + _encode_rel_path(rel)
    elif "playstation" in norm.lower():
        rel = _strip_first_segment_if_matches(norm, "PlayStation")
        return base_urls["PS1"] + _encode_rel_path(rel)
    else:
        return base_urls["DC"] + _encode_rel_path(norm)

@app.route('/')
def index():
    json_data = load_json_file()
    total_games = count_total_games(json_data) if json_data else 0
    return render_template('index.html', total_games=total_games)

# Página de listado de juegos con filtros
@app.route('/games')
def games_page():
    games = build_games_index()
    # Consolas disponibles y conteos
    console_counts = {}
    for g in games:
        for c in g['consoles']:
            console_counts[c] = console_counts.get(c, 0) + 1
    consoles = sorted(console_counts.items(), key=lambda x: x[0])
    total = len(games)
    return render_template('games.html', consoles=consoles, total_games=total)

# API para obtener juegos filtrados/paginados
@app.route('/api/games')
def api_games():
    games = build_games_index()
    q = request.args.get('q', '', type=str).strip().lower()
    console = request.args.get('console', '', type=str).strip()
    page = max(1, request.args.get('page', 1, type=int))
    page_size = min(400, max(10, request.args.get('page_size', 50, type=int)))

    filtered = games
    if console:
        c_l = console.lower()
        filtered = [g for g in filtered if any((cc or '').lower() == c_l for cc in g['consoles'])]
    if q:
        filtered = [g for g in filtered if q in (g['name'] or '').lower()]

    total = len(filtered)
    total_pages = (total + page_size - 1) // page_size if page_size else 1
    if page > total_pages and total_pages > 0:
        page = total_pages
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    return {
        'success': True,
        'items': items,
        'page': page,
        'page_size': page_size,
        'total': total,
        'total_pages': total_pages
    }

@app.route('/dl')
def dl_redirect():
    """Redirige al enlace de descarga a partir de un hash."""
    hash_value = request.args.get('hash', '', type=str)
    data = load_json_file()
    if not data or not hash_value:
        return "Hash no provisto o base de datos no disponible", 400
    rom_path = find_hash_in_json(data, hash_value)
    if not rom_path:
        return f"No se encontró el hash '{hash_value}'", 404
    url = get_download_url(rom_path)
    return redirect(url)

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
