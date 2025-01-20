import requests
import json
import time

# Configuración
API_KEY = "APIKEY"
BASE_URL = "https://retroachievements.org/API/"
PAGE_SIZE = 500  # Máximo número de registros que la API permite obtener por solicitud

# Función para obtener la lista de juegos en "Want to Play" con paginación
def get_want_to_play(username, offset=0, count=PAGE_SIZE):
    url = f"{BASE_URL}API_GetUserWantToPlayList.php?u={username}&y={API_KEY}&c={count}&o={offset}"
    response = requests.get(url)
    print(f"Respuesta de la API para la lista de juegos: {response.status_code}")
    print(f"Contenido de la respuesta: {response.text}")
    return response.json()

# Función para obtener los detalles del juego, incluyendo la consola
def get_game_details(game_id):
    url = f"{BASE_URL}API_GetGame.php?i={game_id}&y={API_KEY}"
    response = requests.get(url)
    return response.json()

# Función para obtener los hashes de un juego
def get_game_hashes(game_id):
    url = f"{BASE_URL}API_GetGameHashes.php?i={game_id}&y={API_KEY}"
    response = requests.get(url)
    return response.json()

# Función para guardar los hashes en un archivo JSON
def save_to_json(data, filename="game_hashes.json"):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

# Función principal para obtener la lista de "Want to Play" y los hashes
def main(username):
    # Obtener la lista de juegos "Want to Play"
    print(f"Obteniendo lista de juegos para el usuario: {username}")
    
    total_games = []
    offset = 0
    while True:
        games = get_want_to_play(username, offset=offset, count=PAGE_SIZE)
        
        if 'Results' not in games or not games['Results']:
            print("No se pudieron obtener más juegos o no hay juegos en la lista.")
            break
        
        total_games.extend(games['Results'])  # Agregar los juegos a la lista total
        offset += PAGE_SIZE  # Avanzamos el offset para la próxima solicitud
        
        # Si ya hemos obtenido todos los juegos, detenemos la paginación
        if len(total_games) >= games['Total']:
            break
        
        # Esperamos un poco entre las solicitudes para evitar sobrecargar el servidor
        time.sleep(1)
    
    print(f"Se han obtenido un total de {len(total_games)} juegos.")
    
    game_data = {}

    # Procesamos cada juego y obtenemos sus hashes y detalles
    for game in total_games:
        game_id = game['ID']
        game_title = game['Title']
        
        print(f"Consultando detalles y hashes para el juego: {game_title} (ID: {game_id})")
        
        # Obtener los detalles del juego, incluyendo la consola
        game_details = get_game_details(game_id)
        
        if 'ConsoleName' not in game_details:
            print(f"No se pudo obtener la consola para el juego: {game_title}")
            continue
        
        console_name = game_details['ConsoleName']
        
        # Obtener los hashes del juego
        game_hashes = get_game_hashes(game_id)
        
        if 'Results' not in game_hashes:
            print(f"Error obteniendo hashes para el juego: {game_title}")
            continue
        
        # Agregar la información al diccionario
        game_data[game_title] = {
            "console": console_name,  # Agregar el nombre de la consola
            "regions": {},
            "languages": {}
        }

        # Clasificamos los hashes por región y idioma
        for result in game_hashes['Results']:
            # Asegurarse de que result['Name'] no sea None
            if result['Name'] is None:
                print(f"Se omitió un hash con 'Name' nulo: {result}")
                continue  # Saltamos este resultado si el nombre es nulo
            # Inicializar la región y el idioma
            regions = []
            languages = []

            # Verificamos si el juego es World (para múltiples regiones)
            if 'World' in result['Name']:
                regions.append("WORLD")

            # Determinar la región (Evitar incluir en USA/EUR si tiene (Ru))
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

            # Agregar la información al diccionario de regiones y/o idiomas
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
        
        # Esperamos un poco entre las solicitudes para evitar sobrecargar el servidor
        time.sleep(1)

    # Guardamos la información en un archivo JSON
    save_to_json(game_data)
    print(f"Información guardada en 'game_hashes.json'.")

# Llamamos a la función principal pasando tu nombre de usuario de RetroAchievements
if __name__ == "__main__":
    username = "Pipetboy"  # Cambia esto por tu nombre de usuario de RetroAchievements
    main(username)
