"""
Genera Data/retroachievements_metadata.json cruzando nuestra coleccion
contra el catalogo de RetroAchievements (titulos reales, caratulas,
cantidad de logros, y el set de hashes que RA reconoce).
Requiere API_KEY en .env (ver ejemplo.env).
"""
from src.core.games_metadata_sync import GamesMetadataSync


def main():
    GamesMetadataSync().run()


if __name__ == "__main__":
    main()
