import json
import requests
import webbrowser

# URL del archivo JSON que contiene los hashes
JSON_URL = "https://archive.org/download/retroachievements_collection_v5/TamperMonkeyRetroachievements.json"

# Función para descargar el archivo JSON desde archive.org
def download_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error para códigos de estado 4xx o 5xx
        return response.json()  # Devolvemos el contenido como un objeto JSON
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP al descargar el archivo JSON: {http_err}")
    except Exception as err:
        print(f"Error al descargar el archivo JSON: {err}")
    return None

# Función para buscar el hash en el archivo JSON
def find_hash_in_json(json_data, hash_value):
    for game_id, hash_list in json_data.items():
        for item in hash_list:
            if hash_value.upper() in item:
                print(f"Hash encontrado: {item}")  # Mensaje de depuración
                return item[hash_value.upper()]  # Devolver la ruta del archivo ROM
    return None

# Función para abrir la URL en el navegador
def open_url_in_browser(url):
    print(f"Abriendo {url} en el navegador...")
    webbrowser.open(url)

# Función principal
def main():
    # Hash predefinido para la depuración
    hash_value = "eb7c9ef37db8a4269bdb55d7d37d2744"

    # Descargar el archivo JSON
    print("Descargando archivo JSON...")
    json_data = download_json(JSON_URL)
    
    if json_data:
        # Buscar el hash en el archivo JSON
        print(f"Buscando el hash {hash_value} en el archivo JSON...")
        rom_path = find_hash_in_json(json_data, hash_value)

        if rom_path:
            # Si el hash se encuentra, abrimos la URL de descarga en el navegador
            base_url = "https://archive.org/download/retroachievements_collection_v5/"
            download_url = base_url + rom_path.replace("\\", "/").replace(" ", "%20")
            print(f"Hash encontrado. La URL de descarga es: {download_url}")
            open_url_in_browser(download_url)
        else:
            print(f"Hash {hash_value} no encontrado en el archivo JSON.")
    else:
        print("No se pudo descargar o procesar el archivo JSON.")

# Ejecutar el programa
if __name__ == "__main__":
    main()
