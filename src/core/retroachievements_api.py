"""
Cliente minimo para la Web API de RetroAchievements.
https://api-docs.retroachievements.org/
"""
import time
from typing import Any, Dict, List

import requests

BASE_URL = "https://retroachievements.org/API"
MAX_ATTEMPTS = 3  # shortcut: retries fijos sin backoff exponencial, alcanza para timeouts transitorios


class RetroAchievementsAPIError(Exception):
    """Error al llamar a la API de RetroAchievements."""
    pass


class RetroAchievementsClient:
    """Wrapper fino sobre los endpoints que necesitamos de la Web API de RA."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get(self, endpoint: str, params: Dict[str, Any]) -> Any:
        params = {**params, "y": self.api_key}
        last_error = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=15)
            except requests.RequestException as e:
                last_error = f"{endpoint}: error de red ({e})"
                if attempt < MAX_ATTEMPTS:
                    time.sleep(1)
                continue
            if response.status_code != 200:
                raise RetroAchievementsAPIError(
                    f"{endpoint} devolvio status {response.status_code}: {response.text[:200]}"
                )
            return response.json()
        raise RetroAchievementsAPIError(f"{last_error} (despues de {MAX_ATTEMPTS} intentos)")

    def get_want_to_play_list(self, username: str) -> List[Dict[str, Any]]:
        """Trae la lista completa de 'Want to Play' del usuario (pagina sola)."""
        results: List[Dict[str, Any]] = []
        offset = 0
        page_size = 500
        while True:
            data = self._get(
                "API_GetUserWantToPlayList.php",
                {"u": username, "c": page_size, "o": offset},
            )
            page = data.get("Results", [])
            results.extend(page)
            total = data.get("Total", len(results))
            offset += len(page)
            if not page or offset >= total:
                break
        return results

    def get_game_hashes(self, game_id: int) -> List[Dict[str, Any]]:
        """Trae los hashes (MD5 + nombre de archivo) asociados a un juego."""
        data = self._get("API_GetGameHashes.php", {"i": game_id})
        return data.get("Results", [])

    def get_console_ids(self) -> List[Dict[str, Any]]:
        """Trae todos los sistemas/consolas conocidos por RA (ID, Name)."""
        return self._get("API_GetConsoleIDs.php", {})

    def get_game_list(self, console_id: int, with_hashes: bool = True) -> List[Dict[str, Any]]:
        """Trae todos los juegos de una consola. Con with_hashes=True cada juego
        incluye su lista de hashes MD5 (campo 'Hashes') en la misma llamada."""
        return self._get(
            "API_GetGameList.php",
            {"i": console_id, "h": 1 if with_hashes else 0},
        )
