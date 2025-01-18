import json
import subprocess
from rich.console import Console
from rich.prompt import Prompt

# URL del archivo JSON que contiene los hashes
JSON_FILE_PATH = "game_hashes.json"  # Suponemos que este es el archivo JSON generado por el primer script

# Inicializar consola de Rich
console = Console()

# Función para cargar el JSON desde el archivo
def load_json(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[bold red]Error al cargar el archivo JSON: {e}[/bold red]")
        return {}

# Función para mostrar las consolas disponibles
def list_consoles(json_data: dict) -> list:
    consoles = set()  # Usamos un conjunto para evitar duplicados
    for game in json_data.values():
        console_name = game.get("console")
        if console_name:
            consoles.add(console_name)
    return list(consoles)

# Función para seleccionar una consola
def select_console(consoles: list) -> str:
    console.print("Seleccione una consola para descargar el juego:", style="bold blue")
    for i, console_name in enumerate(consoles, 1):
        console.print(f"{i}. {console_name}", style="bold cyan")
    
    choice = Prompt.ask("Ingrese el número de la consola que desea seleccionar", default="1", show_default=True)
    
    try:
        console_name = consoles[int(choice) - 1]
        return console_name
    except (ValueError, IndexError):
        console.print("[bold red]Selección no válida. Usando la primera consola por defecto.[/bold red]")
        return consoles[0]

# Función para listar los juegos de una consola seleccionada
def list_games_for_console(json_data: dict, console_name: str) -> list:
    games = [game_name for game_name, game_data in json_data.items() if game_data["console"] == console_name]
    return games

# Función para seleccionar un juego dentro de la consola seleccionada
def select_game(games: list) -> str:
    console.print("Seleccione un juego para descargar:", style="bold blue")
    for i, game_name in enumerate(games, 1):
        console.print(f"{i}. {game_name}", style="bold cyan")
    # Agregar la opción para seleccionar "todos"
    console.print(f"{len(games) + 1}. Todos", style="bold cyan")

    choice = Prompt.ask("Ingrese el número del juego que desea seleccionar", default="1", show_default=True)
    
    try:
        if choice == str(len(games) + 1):  # Si se elige "todos"
            return "todos"
        game_name = games[int(choice) - 1]
        return game_name
    except (ValueError, IndexError):
        console.print("[bold red]Selección no válida. Usando el primer juego por defecto.[/bold red]")
        return games[0]

# Función para seleccionar la región y obtener los hashes
def select_region_and_hash(json_data: dict, game_name: str) -> str:
    regions = json_data[game_name]["regions"]
    console.print(f"Regiones disponibles para {game_name}:", style="bold blue")
    
    for region in regions:
        console.print(f"- {region}", style="bold cyan")
    
    region = Prompt.ask("Ingrese la región que desea seleccionar", choices=list(regions.keys()))
    
    # Convertir la entrada a mayúsculas para hacerla insensible a mayúsculas/minúsculas
    region = region.strip().upper()

    hashes = regions[region]
    
    # Mostrar los hashes disponibles
    console.print(f"Seleccione un hash para la región {region}:", style="bold blue")
    for i, hash_data in enumerate(hashes, 1):
        console.print(f"{i}. {hash_data['name']} - Hash: {hash_data['hash']}", style="bold cyan")
    
    choice = Prompt.ask("Ingrese el número del hash que desea seleccionar", default="1", show_default=True)
    
    try:
        hash_value = hashes[int(choice) - 1]['hash']
        return hash_value
    except (ValueError, IndexError):
        console.print("[bold red]Selección no válida. Usando el primer hash por defecto.[/bold red]")
        return hashes[0]['hash']

# Función principal
def main() -> None:
    # Cargar el archivo JSON
    json_data = load_json(JSON_FILE_PATH)

    if not json_data:
        return

    # Listar las consolas disponibles
    consoles = list_consoles(json_data)
    
    # Seleccionar una consola
    console_name = select_console(consoles)
    
    # Listar los juegos de la consola seleccionada
    games = list_games_for_console(json_data, console_name)
    
    # Seleccionar un juego
    game_name = select_game(games)

    if game_name == "todos":  # Si se seleccionó "todos"
        for game in games:
            hash_value = select_region_and_hash(json_data, game)
            if hash_value:
                console.print(f"Hash seleccionado: {hash_value}", style="bold green")
                try:
                    subprocess.run(["python", "Descargar.py", hash_value], check=True)
                except subprocess.CalledProcessError as e:
                    console.print(f"[bold red]Error al ejecutar el script de descarga: {e}[/bold red]")
        return
    
    else:
        # Seleccionar una región y obtener el hash
        hash_value = select_region_and_hash(json_data, game_name)

        if hash_value:
            console.print(f"Hash seleccionado: {hash_value}", style="bold green")
            
            # Llamar al segundo script (descargar.py) con el hash como argumento
            try:
                subprocess.run(["python", "Descargar.py", hash_value], check=True)
            except subprocess.CalledProcessError as e:
                console.print(f"[bold red]Error al ejecutar el script de descarga: {e}[/bold red]")

# Ejecutar el programa
if __name__ == "__main__":
    main()
