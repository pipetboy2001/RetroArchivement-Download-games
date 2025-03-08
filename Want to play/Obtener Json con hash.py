import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
USERNAME = os.getenv("USERNAME")
BASE_URL = "https://retroachievements.org/API/"
PAGE_SIZE = 500  

def get_want_to_play(username, offset=0, count=PAGE_SIZE):
    url = f"{BASE_URL}API_GetUserWantToPlayList.php?u={username}&y={API_KEY}&c={count}&o={offset}"
    response = requests.get(url)
    print(f"Respuesta de la API para la lista de juegos: {response.status_code}")
    print(f"Contenido de la respuesta: {response.text}")
    return response.json()

def get_game_details(game_id):
    url = f"{BASE_URL}API_GetGame.php?i={game_id}&y={API_KEY}"
    response = requests.get(url)
    return response.json()

def get_game_hashes(game_id):
    url = f"{BASE_URL}API_GetGameHashes.php?i={game_id}&y={API_KEY}"
    response = requests.get(url)
    return response.json()

def save_to_json(data, filename="game_hashes.json"):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

def main(username):
    print(f"Obteniendo lista de juegos para el usuario: {username}")
    
    total_games = []
    offset = 0
    while True:
        games = get_want_to_play(username, offset=offset, count=PAGE_SIZE)
        
        if 'Results' not in games or not games['Results']:
            print("No se pudieron obtener más juegos o no hay juegos en la lista.")
            break
        total_games.extend(games['Results'])  
        offset += PAGE_SIZE
        if len(total_games) >= games['Total']:
            break
        time.sleep(1)
    
    print(f"Se han obtenido un total de {len(total_games)} juegos.")
    game_data = {}
    for game in total_games:
        game_id = game['ID']
        game_title = game['Title']
        
        print(f"Consultando detalles y hashes para el juego: {game_title} (ID: {game_id})")
        game_details = get_game_details(game_id)
        
        if 'ConsoleName' not in game_details:
            print(f"No se pudo obtener la consola para el juego: {game_title}")
            continue
        
        console_name = game_details['ConsoleName']
        game_hashes = get_game_hashes(game_id)
        
        if 'Results' not in game_hashes:
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
    print(f"Información guardada en 'game_hashes.json'.")

if __name__ == "__main__":
    username = USERNAME  # Cambia esto por tu nombre de usuario de RetroAchievements
    main(username)
