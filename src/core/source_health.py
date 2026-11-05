"""
Logica para el chequeo periodico de salud de las fuentes de descarga: por
cada consola, toma una muestra al azar de ROMs y prueba si su URL real
(la que generaria la app) responde. Separado de check_sources_health.py
(el CLI) para poder testear la logica pura -- agrupacion y umbral -- sin
pegarle a la red.
"""
import json
import random
from collections import defaultdict
from typing import Dict, List, Tuple

import config
from .link_checker import is_download_url_reachable
from .rom_info import get_console_from_rom_path
from ..factories.url_factory import URLGeneratorFactory


def group_roms_by_console(data: dict) -> Dict[str, List[str]]:
    """{consola: [rom_path, ...]} a partir de la estructura cruda de
    TamperMonkeyRetroachievements.json ({game_id: [{hash: rom_path}, ...]})."""
    roms: Dict[str, List[str]] = defaultdict(list)
    for versions in data.values():
        for entry in versions:
            for rom_path in entry.values():
                roms[get_console_from_rom_path(rom_path)].append(rom_path)
    return roms


def _status(reachable: int, total: int, threshold: float) -> Tuple[str, float]:
    pct = reachable / total if total else 0.0
    return ("OK" if pct >= threshold else "ROTO"), pct


def run(sample_size: int = 15, threshold: float = 0.5) -> Tuple[str, bool]:
    """Devuelve (reporte en texto, hay_alguna_rota)."""
    with open(config.JSON_FILE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    roms_by_console = group_roms_by_console(data)

    lines = []
    any_broken = False
    for console in sorted(roms_by_console):
        # shortcut: consolas con pocas ROMs quedan con una muestra chica (mas
        # ruidosa); si eso da falsos positivos seguidos, subir sample_size.
        candidates = roms_by_console[console]
        sample = random.sample(candidates, min(sample_size, len(candidates)))
        reachable = sum(
            1 for rom_path in sample
            if is_download_url_reachable(URLGeneratorFactory.generate_url(rom_path))
        )
        status, pct = _status(reachable, len(sample), threshold)
        if status == "ROTO":
            any_broken = True
        lines.append(f"- {console}: {reachable}/{len(sample)} alcanzables ({pct:.0%}) -- {status}")

    return "\n".join(lines), any_broken


if __name__ == "__main__":
    assert _status(8, 10, 0.5) == ("OK", 0.8)
    assert _status(2, 10, 0.5) == ("ROTO", 0.2)
    assert _status(0, 0, 0.5) == ("ROTO", 0.0)

    fixture = {
        "1": [{"HASHA": "SNES-Super Famicom/Game/Game (U).sfc"}],
        "2": [{"HASHB": "PlayStation 2/A-M/Game (U).iso"}],
    }
    grouped = group_roms_by_console(fixture)
    assert grouped["SNES"] == ["SNES-Super Famicom/Game/Game (U).sfc"]
    assert grouped["PS2"] == ["PlayStation 2/A-M/Game (U).iso"]

    print("source_health smoke check: OK")
