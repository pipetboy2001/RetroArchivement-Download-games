"""
Genera game_hashes.json a partir de la lista "Want to Play" real del usuario
en RetroAchievements, cruzando cada hash contra la coleccion descargable
(Data/TamperMonkeyRetroachievements.json) para saber si existe y en que
region quedo.
"""
import json
import os
import sys
import time

from dotenv import load_dotenv

import config
from .data_manager import RetroAchievementsDataManager
from .retroachievements_api import RetroAchievementsClient, RetroAchievementsAPIError
from .rom_info import analyze_rom_info
from ..utils.helpers import UIHelper

DELAY_BETWEEN_GAMES = 0.4  # shortcut: pausa fija sin backoff, ver plan


def _safe_console_text(text: str) -> str:
    """Evita UnicodeEncodeError en consolas Windows (cp1252) con titulos
    que traen caracteres fuera de ese charset (acentos japoneses, etc)."""
    encoding = sys.stdout.encoding or "utf-8"
    return text.encode(encoding, errors="replace").decode(encoding)


def _bucket_region(rom_path: str) -> str:
    """Mapea un rom_path a una de las claves de config.PREFERRED_REGIONS.

    shortcut: heuristica de 4 reglas sobre el nombre de archivo, no cubre
    todos los tags estilo No-Intro; si aparecen juegos mal clasificados,
    ampliar esta funcion.
    """
    filename = rom_path.split('/')[-1] if '/' in rom_path else rom_path
    if "[T+Spa]" in filename or "(Spain)" in filename:
        return "ES"

    region = analyze_rom_info(rom_path)["region"]
    if region == "USA":
        return "USA"
    if region == "Europe":
        return "EUROPE"
    if region == "Japan":
        return "JPN"
    return "WORLD"


class WantToPlaySync:
    """Orquesta la sincronizacion de game_hashes.json contra la API de RA."""

    def __init__(self):
        self.ui = UIHelper()
        self.data_manager = RetroAchievementsDataManager()

    def run(self):
        load_dotenv(config.ENV_FILE)
        api_key = os.getenv("API_KEY")
        username = os.getenv("RETROACHIEVEMENTS_USERNAME")

        if not api_key or not username:
            self.ui.display_error_message(
                f"Falta API_KEY o RETROACHIEVEMENTS_USERNAME en {config.ENV_FILE}. "
                f"Copia {config.ENV_EXAMPLE_FILE} y completa tus credenciales."
            )
            return

        client = RetroAchievementsClient(api_key)

        self.ui.display_info_message(f"Buscando lista 'Want to Play' de {username}...")
        try:
            want_to_play = client.get_want_to_play_list(username)
        except RetroAchievementsAPIError as e:
            self.ui.display_error_message(f"No se pudo obtener la lista 'Want to Play': {e}")
            return

        self.ui.display_info_message(f"{len(want_to_play)} juegos en la lista. Consultando hashes...")

        result = {}
        games_without_hashes = []
        total = len(want_to_play)

        for i, game in enumerate(want_to_play):
            if i > 0:
                time.sleep(DELAY_BETWEEN_GAMES)

            title = game.get("Title", f"Game {game.get('ID')}")
            print(f"[{i + 1}/{total}] {_safe_console_text(title)}")
            try:
                hashes = client.get_game_hashes(game["ID"])
            except RetroAchievementsAPIError as e:
                self.ui.display_error_message(_safe_console_text(f"{title}: {e}"))
                games_without_hashes.append(title)
                continue

            regions = {}
            for h in hashes:
                md5 = h.get("MD5")
                if not md5:
                    continue
                rom_path = self.data_manager.find_hash(md5)
                if not rom_path:
                    continue  # no lo tenemos en la coleccion descargable
                bucket = _bucket_region(rom_path)
                regions.setdefault(bucket, []).append({"name": h.get("Name", ""), "hash": md5})

            if regions:
                result[title] = {"console": game.get("ConsoleName", "Unknown"), "regions": regions}
            else:
                games_without_hashes.append(title)

        with open(config.WANT_TO_PLAY_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        self.ui.display_success_message(
            f"{config.WANT_TO_PLAY_FILE} actualizado: {len(result)} juegos con hashes descargables."
        )
        if games_without_hashes:
            self.ui.display_info_message(
                f"{len(games_without_hashes)} juegos sin ningun hash descargable: "
                + _safe_console_text(", ".join(games_without_hashes))
            )


if __name__ == "__main__":
    assert _bucket_region("Genesis-Mega Drive/Foo/Foo (U) [T+Spa].zip") == "ES"
    assert _bucket_region("Genesis-Mega Drive/Foo/Foo (U) [!].zip") == "USA"
    assert _bucket_region("Genesis-Mega Drive/Foo/Foo (E) [!].zip") == "EUROPE"
    assert _bucket_region("Genesis-Mega Drive/Foo/Foo (J) [!].zip") == "JPN"
    assert _bucket_region("Genesis-Mega Drive/Foo/Foo [!].zip") == "WORLD"
    print("want_to_play_sync smoke check: OK")
