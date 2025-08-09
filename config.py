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

## URLs base para diferentes consolas
BASE_URLS = {
    "ARCADE": "https://archive.org/download/fbnarcade-fullnonmerged/arcade/",
    "SNES": "https://archive.org/download/retroachievements_collection_SNES-Super_Famicom/",
    "NES": "https://archive.org/download/retroachievements_collection_NES-Famicom/",
    "PSP": "https://dn720005.ca.archive.org/0/items/retroachievements_collection_PlayStation_Portable/PlayStation%20Portable/",
    "PS1": "https://archive.org/download/retroachievements_collection_PlayStation/PlayStation/",
    "PS2_A_M": "https://archive.org/download/retroachievements_collection_PlayStation_2_A-M/PlayStation%202/",
    "PS2_N_Z": "https://archive.org/download/retroachievements_collection_PlayStation_2_N-Z/PlayStation%202/",
    "DC": "https://archive.org/download/retroachievements_collection_v5/"
}

## Configuración de validación
MIN_HASH_LENGTH = 8
MAX_DOWNLOAD_ATTEMPTS = 5
