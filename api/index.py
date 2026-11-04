from flask import Flask, render_template, request, redirect, url_for, flash
import webbrowser
import os
import sys

# Permite importar el paquete src/ (core de dominio compartido con la app de
# consola) cuando este archivo corre como función serverless en Vercel.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.data_manager import RetroAchievementsDataManager
from src.core.rom_info import get_console_from_rom_path, extract_game_name, analyze_rom_info
from src.factories.url_factory import URLGeneratorFactory
from src.core.link_checker import is_download_url_reachable, is_hash_recognized_by_ra

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para usar flash

# Ruta al archivo JSON local
JSON_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'TamperMonkeyRetroachievements.json')
RA_METADATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'retroachievements_metadata.json')

data_manager = RetroAchievementsDataManager(json_file_path=JSON_FILE_PATH)
cached_games_index = None  # Índice cacheado para listados
cached_ra_metadata = None  # {game_id: {id, title, image_icon, achievements}}, generado por sync_games_metadata.py

# Cargar el archivo JSON local
def load_json_file():
    return data_manager.load_data()

def load_ra_metadata():
    """Carga Data/retroachievements_metadata.json (titulos/caratulas/logros reales).
    Si no existe todavia (no se corrio sync_games_metadata.py), /games sigue
    funcionando sin esos datos."""
    global cached_ra_metadata
    if cached_ra_metadata is None:
        try:
            import json
            with open(RA_METADATA_FILE, 'r', encoding='utf-8') as f:
                cached_ra_metadata = json.load(f).get('games', {})
        except (FileNotFoundError, ValueError):
            cached_ra_metadata = {}
    return cached_ra_metadata

# Función para contar total de juegos en la base de datos (optimizada)
def count_total_games(json_data):
    # Simplemente contar el número de IDs únicos de juegos
    return len(json_data) if json_data else 0

# Construir índice de juegos para listados/filtrado
def build_games_index():
    global cached_games_index
    if cached_games_index is not None:
        return cached_games_index
    data = load_json_file()
    if not data:
        cached_games_index = []
        return cached_games_index
    ra_metadata = load_ra_metadata()
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
        ra_info = ra_metadata.get(game_id)
        games.append({
            'id': game_id,
            'name': game_name or f'Game {game_id}',
            'consoles': sorted(list(consoles)),
            'versions': total_versions,
            'sample_rom_path': sample_rom_path,
            'image_icon': ra_info.get('image_icon') if ra_info else None,
            'achievements': ra_info.get('achievements') if ra_info else None,
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
    return data_manager.find_hash(hash_value)

# Función para obtener la URL de descarga
def get_download_url(rom_path: str) -> str:
    return URLGeneratorFactory.generate_url(rom_path)

@app.route('/')
def index():
    json_data = load_json_file()
    total_games = count_total_games(json_data) if json_data else 0
    return render_template('index.html', total_games=total_games)

# Consolas disponibles y conteos (usado por /games y /api/games)
def _console_counts(games):
    console_counts = {}
    for g in games:
        for c in g['consoles']:
            console_counts[c] = console_counts.get(c, 0) + 1
    return sorted(console_counts.items(), key=lambda x: x[0])

# Página de listado de juegos con filtros
@app.route('/games')
def games_page():
    games = build_games_index()
    consoles = _console_counts(games)
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
        'total_pages': total_pages,
        'consoles': [{'name': c, 'count': n} for c, n in _console_counts(games)]
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
            return {
                'success': True,
                'download_url': download_url,
                'link_ok': is_download_url_reachable(download_url),
                'ra_recognized': is_hash_recognized_by_ra(search_term),
            }
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

# Página de FAQ y Aviso legal
@app.route('/faq')
def faq():
    total_games = len(build_games_index()) if build_games_index() else 0
    return render_template('faq.html', total_games=total_games)

if __name__ == '__main__':
    app.run(debug=True)
