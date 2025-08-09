import os
import requests
import json
import time
import signal
import sys
from dotenv import load_dotenv

# Variable global para manejar interrupciones
interrupted = False

def signal_handler(sig, frame):
    global interrupted
    print('\n\n⚠️  Interrupción detectada. Guardando progreso...')
    interrupted = True

load_dotenv()

API_KEY = os.getenv("API_KEY")
USERNAME = os.getenv("RETROACHIEVEMENTS_USERNAME")
BASE_URL = "https://retroachievements.org/API/"
PAGE_SIZE = 500

# Verificar que las credenciales estén cargadas correctamente
if not API_KEY or not USERNAME:
    print("Error: No se pudieron cargar las credenciales del archivo .env")
    print(f"API_KEY encontrado: {'Sí' if API_KEY else 'No'}")
    print(f"USERNAME encontrado: {'Sí' if USERNAME else 'No'}")
    exit(1)

print(f"Credenciales cargadas - Usuario: {USERNAME}")  

def get_want_to_play(username, offset=0, count=PAGE_SIZE):
    url = f"{BASE_URL}API_GetUserWantToPlayList.php?u={username}&y={API_KEY}&c={count}&o={offset}"
    print(f"URL de la API: {url}")
    response = requests.get(url)
    print(f"Respuesta de la API para la lista de juegos: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error en la API: {response.status_code}")
        print(f"Contenido de la respuesta: {response.text}")
        return None
    
    try:
        return response.json()
    except json.JSONDecodeError:
        print("Error: La respuesta no es un JSON válido")
        print(f"Contenido: {response.text}")
        return None

def get_game_details(game_id):
    url = f"{BASE_URL}API_GetGame.php?i={game_id}&y={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code} obteniendo detalles para juego ID {game_id}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión obteniendo detalles para juego ID {game_id}: {e}")
        return None

def get_game_hashes(game_id):
    url = f"{BASE_URL}API_GetGameHashes.php?i={game_id}&y={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code} obteniendo hashes para juego ID {game_id}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión obteniendo hashes para juego ID {game_id}: {e}")
        return None

def save_to_json(data, filename="game_hashes.json"):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

def main(username):
    global interrupted
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"Obteniendo lista de juegos para el usuario: {username}")
    print("💡 Presiona Ctrl+C para interrumpir y guardar el progreso actual")
    
    total_games = []
    offset = 0
    while True:
        games = get_want_to_play(username, offset=offset, count=PAGE_SIZE)
        
        if games is None or 'Results' not in games or not games['Results']:
            print("No se pudieron obtener más juegos o no hay juegos en la lista.")
            break
        total_games.extend(games['Results'])  
        offset += PAGE_SIZE
        if len(total_games) >= games['Total']:
            break
        time.sleep(1)
    
    print(f"Se han obtenido un total de {len(total_games)} juegos.")
    game_data = {}
    processed_count = 0
    
    for game in total_games:
        if interrupted:
            print(f"\n🛑 Proceso interrumpido. Se procesaron {processed_count} de {len(total_games)} juegos.")
            break
            
        game_id = game['ID']
        game_title = game['Title']
        processed_count += 1
        
        print(f"[{processed_count}/{len(total_games)}] Consultando: {game_title} (ID: {game_id})")
        game_details = get_game_details(game_id)
        
        if game_details is None or 'ConsoleName' not in game_details:
            print(f"No se pudo obtener la consola para el juego: {game_title}")
            continue
        
        console_name = game_details['ConsoleName']
        game_hashes = get_game_hashes(game_id)
        
        if game_hashes is None or 'Results' not in game_hashes:
            print(f"Error obteniendo hashes para el juego: {game_title}")
            continue
        game_data[game_title] = {
            "console": console_name,  # Agregar el nombre de la consola
            "regions": {},
            "languages": {}
        }

        for result in game_hashes['Results']:
            # Asegurarse de que result['Name'] no sea None
            if result['Name'] is None:
                print(f"Se omitió un hash con 'Name' nulo: {result}")
                continue 
            # Inicializar la región y el idioma
            regions = []
            languages = []

            if 'World' in result['Name']:
                regions.append("WORLD")
            if '(Ru)' in result['Name']:
                regions.append("RU")
                
            elif 'USA' in result['Name']:
                regions.append("USA")
            elif 'Europe' in result['Name'] or 'EUR' in result['Name']:
                regions.append("EUR")
            elif 'Japan' in result['Name']:
                regions.append("JPN")
            elif 'Korea' in result['Name']:
                regions.append("KOR")

            # Determinar el idioma
            if 'En' in result['Name']:
                languages.append("EN")
            if 'Es' in result['Name']:
                languages.append("ES")
            if 'Fr' in result['Name']:
                languages.append("FR")
            if 'Pt' in result['Name']:
                languages.append("PT")

            for region in regions:
                if region not in game_data[game_title]["regions"]:
                    game_data[game_title]["regions"][region] = []
                game_data[game_title]["regions"][region].append({
                    "hash": result['MD5'],
                    "name": result['Name']
                })
            
            for language in languages:
                if language not in game_data[game_title]["languages"]:
                    game_data[game_title]["languages"][language] = []
                game_data[game_title]["languages"][language].append({
                    "hash": result['MD5'],
                    "name": result['Name']
                })
        time.sleep(1)
    
    save_to_json(game_data)
    if interrupted:
        print(f"✅ Progreso guardado. Se procesaron {processed_count} juegos de {len(total_games)} total.")
    else:
        print(f"✅ ¡Completado! Información de {len(game_data)} juegos guardada en 'game_hashes.json'.")

if __name__ == "__main__":
    username = USERNAME  # Cambia esto por tu nombre de usuario de RetroAchievements
    main(username)
