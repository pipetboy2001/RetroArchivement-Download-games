"""
Cliente minimo para la Web API de RetroAchievements.
https://api-docs.retroachievements.org/
"""
from typing import List, Dict, Any

import requests

BASE_URL = "https://retroachievements.org/API"


class RetroAchievementsAPIError(Exception):
    """Error al llamar a la API de RetroAchievements."""
    pass


class RetroAchievementsClient:
    """Wrapper fino sobre los endpoints que necesitamos de la Web API de RA."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        params = {**params, "y": self.api_key}
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=15)
        if response.status_code != 200:
            raise RetroAchievementsAPIError(
                f"{endpoint} devolvio status {response.status_code}: {response.text[:200]}"
            )
        return response.json()

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
