# Configuración para RetroAchievements Downloader

## Rutas de archivos
JSON_FILE_PATH = "Data/TamperMonkeyRetroachievements.json"
WANT_TO_PLAY_FILE = "game_hashes.json"
MISSING_GAMES_FILE = "missing_games.txt"
ENV_FILE = ".env"
ENV_EXAMPLE_FILE = "ejemplo.env"

## Preferencias de región (orden de prioridad)
PREFERRED_REGIONS = {
    "ES": 1,      # Español tiene la mayor prioridad
    "USA": 2,     # Luego USA
    "WORLD": 3,   # El resto del mundo
    "EUROPE": 4,  # Luego Europa
    "JPN": 5      # Por último Japón
}

## Configuración de validación
MIN_HASH_LENGTH = 8
