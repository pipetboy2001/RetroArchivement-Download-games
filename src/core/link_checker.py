"""
Verificaciones livianas de si un hash/URL "funciona de verdad":
- el link de descarga generado responde (no esta roto en archive.org)
- el hash es uno que RetroAchievements reconoce (Data/retroachievements_metadata.json)
"""
import json
from typing import Optional, Set

import requests

METADATA_FILE = "Data/retroachievements_metadata.json"

_recognized_hashes: Optional[Set[str]] = None


def is_download_url_reachable(url: str) -> bool:
    """HEAD a la URL de descarga. Nunca levanta excepcion: ante cualquier
    error de red se asume no-alcanzable en vez de romper el flujo de descarga.

    archive.org devuelve 401 para archivos que existen pero requieren login
    en el navegador (ver FAQ del proyecto) - eso NO significa que el link
    este roto, asi que solo 404/410 (confirmado no existe) cuentan como tal.
    """
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code not in (404, 410)
    except requests.RequestException:
        return False


def is_hash_recognized_by_ra(hash_value: str) -> bool:
    """True si el hash aparece en el set de hashes que RA reconoce
    (generado por sync_games_metadata.py). Si el archivo no existe
    todavia, devuelve False en vez de romper."""
    global _recognized_hashes
    if _recognized_hashes is None:
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            _recognized_hashes = set(data.get("recognized_hashes", []))
        except (FileNotFoundError, json.JSONDecodeError):
            _recognized_hashes = set()
    return hash_value.upper() in _recognized_hashes


if __name__ == "__main__":
    assert is_download_url_reachable("https://archive.org/") is True
    # 404 real (archivo inexistente DENTRO de un item que si existe)
    assert is_download_url_reachable(
        "https://archive.org/download/retroachievements_collection_v5/Genesis-Mega%20Drive/ThisFileDoesNotExist123456.zip"
    ) is False
    # 401 (el archivo existe pero pide login en archive.org) debe contar como "reachable"
    assert is_download_url_reachable(
        "https://archive.org/download/retroachievements_collection_v5/Genesis-Mega%20Drive/"
        "Sonic%20the%20Hedgehog/Sonic%20The%20Hedgehog%20%28W%29%20%28REV00%29%20%5BT%2BRus_NewGame%5D.zip"
    ) is True
    print("link_checker smoke check: OK")
