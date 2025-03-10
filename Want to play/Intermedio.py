import json
import subprocess
from rich.console import Console
from rich.prompt import Prompt

JSON_FILE_PATH = "game_hashes.json"  

console = Console()

PREFERRED_REGIONS = {
    "ES": 1,  # Español tiene la mayor prioridad
    "USA": 2,  # Luego USA
    "WORLD": 3,  # el resto del mundo
    "EUROPE": 4,  # Luego Europa
    "JPN": 5  # Por último Japón
}

missing_games = []

def load_json(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[bold red]Error al cargar el archivo JSON: {e}[/bold red]")
        return {}

def list_consoles(json_data: dict) -> list:
    consoles = set()
    for game in json_data.values():
        console_name = game.get("console")
        if console_name:
            consoles.add(console_name)
    return list(consoles)

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

def list_games_for_console(json_data: dict, console_name: str) -> list:
    games = [game_name for game_name, game_data in json_data.items() if game_data["console"] == console_name]
    return games

def select_game(games: list) -> str:
    console.print("Seleccione un juego para descargar:", style="bold blue")
    for i, game_name in enumerate(games, 1):
        console.print(f"{i}. {game_name}", style="bold cyan")
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

def select_region_and_hash(json_data: dict, game_name: str) -> str:
    regions = json_data[game_name]["regions"]
    if not regions:
        console.print(f"[bold red]No hay regiones disponibles para {game_name}.[/bold red]")
        missing_games.append(game_name)
        return None
    console.print(f"Regiones disponibles para {game_name}:", style="bold blue")
    for region in regions:
        console.print(f"- {region}", style="bold cyan")
    selected_region = None
    for preferred_region in PREFERRED_REGIONS:
        preferred_region = preferred_region.strip().upper()
        if preferred_region in regions:
            selected_region = preferred_region
            break
    if selected_region:
        console.print(f"Seleccionando la región preferida: {selected_region}", style="bold green")
        hashes = regions[selected_region]
    else:
        selected_region = list(regions.keys())[0]
        console.print(f"Seleccionando la primera región disponible: {selected_region}", style="bold green")
        hashes = regions[selected_region]

    console.print(f"Hashes disponibles para la región {selected_region}:", style="bold blue")
    preferred_hash = None
    for hash_data in hashes:
        if any(preference in hash_data['name'].upper() for preference in PREFERRED_REGIONS.keys()):
            preferred_hash = hash_data['hash']
            console.print(f"Seleccionando hash: {hash_data['name']} - Hash: {preferred_hash}", style="bold green")
    if not preferred_hash:
        missing_games.append(game_name)
        console.print(f"[bold red]No se encontró un hash preferido, añadiendo {game_name} a la lista de juegos faltantes.[/bold red]")
        return None
    return preferred_hash

def main() -> None:
    json_data = load_json(JSON_FILE_PATH)
    if not json_data:
        return
    consoles = list_consoles(json_data)
    console_name = select_console(consoles)
    games = list_games_for_console(json_data, console_name)
    game_name = select_game(games)
    if game_name == "todos": 
        for game in games:
            hash_value = select_region_and_hash(json_data, game)
            if hash_value:
                console.print(f"Hash seleccionado: {hash_value}", style="bold green")
                try:
                    subprocess.run(["python", "Descargar.py", hash_value], check=True)
                except subprocess.CalledProcessError as e:
                    console.print(f"[bold red]Error al ejecutar el script de descarga[/bold red]")
                    missing_games.append(game)
    else:
        hash_value = select_region_and_hash(json_data, game_name)
        if hash_value:
            console.print(f"Hash seleccionado: {hash_value}", style="bold green")
            try:
                subprocess.run(["python", "Descargar.py", hash_value], check=True)
            except subprocess.CalledProcessError as e:
                console.print(f"[bold red]Error al ejecutar el script de descarga: {e}[/bold red]")
                missing_games.append(game_name)
    console.print("[bold green]Proceso completado con éxito[/bold green]")
    if missing_games:
        with open("missing_games.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(missing_games) + "\n")
        console.print(f"[bold red]Lista de juegos faltantes guardada en missing_games.txt[/bold red]")
        
if __name__ == "__main__":
    main()
