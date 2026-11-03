"""
Genera Data/retroachievements_metadata.json: para cada juego de
Data/TamperMonkeyRetroachievements.json, intenta encontrar su equivalente
real en RetroAchievements (titulo, caratula, cantidad de logros) matcheando
por hash exacto, y guarda el set completo de hashes que RA reconoce.

Usa GetGameList(consoleId, h=1), que devuelve TODOS los juegos de una
consola con sus hashes MD5 en una sola llamada (no hace falta pedir los
hashes juego por juego).
"""
import json
import os
import re
import time

from dotenv import load_dotenv

import config
from .retroachievements_api import RetroAchievementsClient, RetroAchievementsAPIError
from .rom_info import get_console_from_rom_path
from ..utils.helpers import UIHelper

DELAY_BETWEEN_CONSOLES = 0.4  # shortcut: pausa fija sin backoff, igual que want_to_play_sync
METADATA_FILE = "Data/retroachievements_metadata.json"
MEDIA_BASE_URL = "https://media.retroachievements.org"

# Nuestros nombres canonicos (rom_info.get_console_from_rom_path) que no
# matchean por normalizacion directa contra el Name de RA, para las
# consolas mas comunes (NES/SNES/PS1/PS2/PSP/N64/etc). El resto de
# consolas sin cobertura se reportan y quedan afuera (shortcut, ver plan).
MANUAL_CONSOLE_ALIASES = {
    "NES": "NES/Famicom",
    "SNES": "SNES/Super Famicom",
    "N64": "Nintendo 64",
    "PS1": "PlayStation",
    "PS2": "PlayStation 2",
    "PSP": "PlayStation Portable",
    "Sega 32X": "32X",
    "Fds": "Famicom Disk System",
    "PC Engine": "PC Engine/TurboGrafx-16",
    "TurboGrafx-16": "PC Engine/TurboGrafx-16",
    "Gamegear": "Game Gear",
}


def _normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()


class GamesMetadataSync:
    """Orquesta la sincronizacion de Data/retroachievements_metadata.json."""

    def __init__(self):
        self.ui = UIHelper()

    def _our_consoles(self) -> set:
        with open(config.JSON_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        consoles = set()
        for hash_list in data.values():
            for item in hash_list:
                for _hash, rom_path in item.items():
                    consoles.add(get_console_from_rom_path(rom_path))
        return consoles

    def _match_consoles_to_ra(self, client: RetroAchievementsClient):
        ra_consoles = client.get_console_ids()
        ra_by_normalized = {_normalize(c["Name"]): c for c in ra_consoles}

        matched = {}  # nuestro nombre canonico -> RA console dict
        unmatched = []
        for our_name in sorted(self._our_consoles()):
            ra_console = ra_by_normalized.get(_normalize(our_name))
            if not ra_console and our_name in MANUAL_CONSOLE_ALIASES:
                ra_console = ra_by_normalized.get(_normalize(MANUAL_CONSOLE_ALIASES[our_name]))
            if ra_console:
                matched[our_name] = ra_console
            else:
                unmatched.append(our_name)
        return matched, unmatched

    def run(self):
        load_dotenv(config.ENV_FILE)
        api_key = os.getenv("API_KEY")
        if not api_key:
            self.ui.display_error_message(
                f"Falta API_KEY en {config.ENV_FILE}. Copia {config.ENV_EXAMPLE_FILE} y completa tus credenciales."
            )
            return

        client = RetroAchievementsClient(api_key)

        self.ui.display_info_message("Matcheando consolas locales contra RetroAchievements...")
        matched, unmatched = self._match_consoles_to_ra(client)
        if unmatched:
            self.ui.display_info_message(
                f"{len(unmatched)} consolas sin cobertura (no matchean por nombre): "
                + ", ".join(unmatched)
            )

        hash_to_ra = {}  # MD5 upper -> {id, title, image_icon, achievements}
        for i, (our_name, ra_console) in enumerate(matched.items()):
            if i > 0:
                time.sleep(DELAY_BETWEEN_CONSOLES)
            print(f"[{i + 1}/{len(matched)}] {our_name} (RA: {ra_console['Name']})")
            try:
                games = client.get_game_list(ra_console["ID"], with_hashes=True)
            except RetroAchievementsAPIError as e:
                self.ui.display_error_message(f"{our_name}: {e}")
                continue

            for game in games:
                info = {
                    "id": game.get("ID"),
                    "title": game.get("Title"),
                    "image_icon": (MEDIA_BASE_URL + game["ImageIcon"]) if game.get("ImageIcon") else None,
                    "achievements": game.get("NumAchievements", 0),
                }
                for md5 in game.get("Hashes") or []:
                    hash_to_ra[md5.upper()] = info

        with open(config.JSON_FILE_PATH, "r", encoding="utf-8") as f:
            our_data = json.load(f)

        games_metadata = {}
        for game_id, hash_list in our_data.items():
            for item in hash_list:
                for md5 in item:
                    ra_info = hash_to_ra.get(md5.upper())
                    if ra_info:
                        games_metadata[game_id] = ra_info
                        break
                if game_id in games_metadata:
                    break

        result = {
            "games": games_metadata,
            "recognized_hashes": sorted(hash_to_ra.keys()),
        }
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        self.ui.display_success_message(
            f"{METADATA_FILE} actualizado: {len(games_metadata)}/{len(our_data)} juegos con metadata de RA, "
            f"{len(hash_to_ra)} hashes reconocidos en total."
        )


if __name__ == "__main__":
    assert _normalize("Genesis/Mega Drive") == _normalize("genesis mega drive")
    assert _normalize("PlayStation 2") == "playstation 2"
    print("games_metadata_sync smoke check: OK")
