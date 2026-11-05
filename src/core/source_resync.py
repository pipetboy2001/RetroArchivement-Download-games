"""
Resincroniza la fuente de descarga de una consola contra un item nuevo de
archive.org, cuando el item viejo murio y el nuevo tiene una estructura de
carpetas/nombres distinta.

No alcanza con comparar nombres de archivo (la nomenclatura puede diferir
entre colecciones) ni con el MD5 que expone la metadata de archive.org (es
el hash del .zip, no el de la ROM que RetroAchievements espera). Por eso
este script descarga cada candidato, lo descomprime, calcula el hash al
estilo RetroAchievements sobre la ROM de adentro, y matchea contra los
hashes que ya tenemos en Data/TamperMonkeyRetroachievements.json. Lo que no
matchea queda listado aparte para resolver a mano.
"""
import hashlib
import io
import json
import os
import sys
import time
import zipfile
from typing import Dict, List, Tuple

import requests

import config
from .rom_info import get_console_from_rom_path, extract_game_name

MAX_ATTEMPTS = 3  # shortcut: reintentos fijos sin backoff, igual que el resto de los sync scripts
REQUEST_TIMEOUT = 30


def _safe_console_text(text: str) -> str:
    try:
        encoding = sys.stdout.encoding or "utf-8"
        return text.encode(encoding, errors="replace").decode(encoding)
    except Exception:
        return text


def _ra_hash(data: bytes, header_modulus: int = 8192) -> str:
    """Hash estilo RetroAchievements: MD5, salvo que el tamano sea 512 bytes
    mas que un multiplo de `header_modulus` (header de copiadora), en cuyo
    caso se ignoran los primeros 512 bytes. La regla (confirmada en
    docs.retroachievements.org) es igual en espiritu para varias consolas
    pero el modulo cambia: SNES/Super Famicom usa 8KB (8192), PC Engine/
    TurboGrafx-16/SuperGrafx (cartucho) usa 128KB (131072)."""
    if len(data) % header_modulus == 512:
        data = data[512:]
    return hashlib.md5(data).hexdigest()


def _get_with_retries(url: str, **kwargs) -> requests.Response:
    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT, **kwargs)
            if response.status_code == 200:
                return response
            last_error = f"status {response.status_code}"
        except requests.RequestException as e:
            last_error = f"error de red ({e})"
        if attempt < MAX_ATTEMPTS:
            time.sleep(1)
    raise RuntimeError(f"{url}: {last_error} (despues de {MAX_ATTEMPTS} intentos)")


class SourceResync:
    """Orquesta el resync de la fuente de descarga de una consola."""

    def __init__(self, console: str, item: str, label: str = None, header_modulus: int = 8192):
        # `console` puede ser una sola consola o varias separadas por coma
        # (ej: "TurboGrafx-16,PC Engine" -- dos valores distintos de
        # get_console_from_rom_path que en la practica son la misma
        # plataforma, por un merge viejo de datos con folders distintos).
        self.consoles = [c.strip() for c in console.split(",")]
        self.item = item
        self.base_url = f"https://archive.org/download/{item}/"
        file_label = (label or self.consoles[0]).lower().replace(" ", "_")
        self.override_file = f"Data/{file_label}_source_override.json"
        self.missing_file = f"Data/{file_label}_missing_sources.txt"
        # Cache de resumen (hash por archivo ya calculado) -- el job puede
        # tardar bastante (un archivo por request a archive.org) y cortarse
        # a mitad de camino, esto evita perder el progreso ya hecho.
        self.cache_file = f"Data/.{file_label}_hash_cache.json"
        self.header_modulus = header_modulus

    # Extensiones de ROM cruda que se hashean directo, sin descomprimir.
    RAW_EXTENSIONS = (".pce", ".sgx", ".sfc", ".smc", ".nes", ".bin", ".gb", ".gbc", ".gba")

    def _fetch_item_files(self) -> List[Tuple[str, int]]:
        """Devuelve [(nombre, tamano)] de los archivos descargables del item
        nuevo (.zip, o ROMs crudas sin comprimir)."""
        response = _get_with_retries(f"https://archive.org/metadata/{self.item}")
        data = response.json()
        return [
            (f["name"], int(f.get("size", 0)))
            for f in data.get("files", [])
            if f.get("name", "").lower().endswith((".zip",) + self.RAW_EXTENSIONS)
        ]

    def _hash_candidate(self, filename: str) -> str | None:
        """Descarga un archivo del item nuevo y devuelve el hash estilo RA
        de la ROM. Si es .zip, extrae el archivo mas grande de adentro;
        si no, hashea el archivo tal cual (ya es la ROM cruda). None si
        algo sale mal (zip corrupto, vacio, etc. -- se reporta y se sigue)."""
        url = self.base_url + requests.utils.quote(filename, safe="")
        try:
            content = _get_with_retries(url).content
            if filename.lower().endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    infos = [i for i in zf.infolist() if not i.is_dir()]
                    if not infos:
                        return None
                    largest = max(infos, key=lambda i: i.file_size)
                    rom_bytes = zf.read(largest)
            else:
                rom_bytes = content
        except (RuntimeError, zipfile.BadZipFile) as e:
            print(f"  [!] {_safe_console_text(filename)}: {e}")
            return None
        return _ra_hash(rom_bytes, self.header_modulus)

    def _load_our_hashes(self) -> Dict[str, str]:
        """{hash: rom_path} de todas las entradas de las consolas pedidas en
        Data/TamperMonkeyRetroachievements.json."""
        with open(config.JSON_FILE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        ours: Dict[str, str] = {}
        for game_id, versions in data.items():
            for item in versions:
                for hash_value, rom_path in item.items():
                    if get_console_from_rom_path(rom_path) in self.consoles:
                        ours[hash_value.upper()] = rom_path
        return ours

    def run(self):
        consoles_label = ", ".join(self.consoles)
        print(f"Resync de {consoles_label} contra el item '{self.item}' de archive.org...")

        our_hashes = self._load_our_hashes()
        print(f"{len(our_hashes)} hashes de {consoles_label} en nuestra base.")

        files = self._fetch_item_files()
        print(f"{len(files)} archivos en el item nuevo. Descargando y hasheando...")

        # filename -> hash (o "" si no se pudo hashear), cacheado en disco por
        # si el job se corta a mitad de camino -- al reiniciar, se saltea lo
        # que ya esta en el cache en vez de volver a descargar todo.
        cache: Dict[str, str] = {}
        if os.path.exists(self.cache_file):
            with open(self.cache_file, encoding="utf-8") as f:
                cache = json.load(f)
            print(f"Retomando desde cache: {len(cache)}/{len(files)} ya hasheados.")

        for i, (filename, _size) in enumerate(files, start=1):
            if filename in cache:
                continue
            print(f"[{i}/{len(files)}] {_safe_console_text(filename)}")
            h = self._hash_candidate(filename) or ""
            cache[filename] = h
            if i % 20 == 0:
                with open(self.cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache, f)

        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f)

        self.write_outputs(cache, our_hashes, partial=False)

    def write_outputs(self, cache: Dict[str, str], our_hashes: Dict[str, str] = None, partial: bool = True):
        """Arma override_file/missing_file a partir de lo que haya en el
        cache en este momento. Se puede llamar con un cache a medio
        terminar (partial=True) para tener un preview mientras el resync
        completo sigue corriendo -- se reescribe igual al final con el
        cache completo."""
        if our_hashes is None:
            our_hashes = self._load_our_hashes()

        new_hash_to_filename: Dict[str, str] = {}
        for filename, h in cache.items():
            if h:
                new_hash_to_filename[h.upper()] = filename

        override: Dict[str, str] = {}
        missing: List[Tuple[str, str, str]] = []  # (nombre, rom_path, hash)
        for hash_value, rom_path in our_hashes.items():
            filename = new_hash_to_filename.get(hash_value)
            if filename:
                override[rom_path] = filename
            else:
                missing.append((extract_game_name(rom_path), rom_path, hash_value))

        os.makedirs("Data", exist_ok=True)
        with open(self.override_file, "w", encoding="utf-8") as f:
            json.dump(override, f, ensure_ascii=False, indent=2, sort_keys=True)

        missing.sort(key=lambda x: x[0].lower())
        with open(self.missing_file, "w", encoding="utf-8") as f:
            for name, rom_path, hash_value in missing:
                f.write(f"{name}\t{rom_path}\t{hash_value}\n")

        total = len(our_hashes)
        matched = len(override)
        pct = (matched / total * 100) if total else 0
        label = "PARCIAL -- resync todavia corriendo" if partial else "final"
        print(f"\n[{label}] {matched}/{total} hashes con match ({pct:.1f}%).")
        print(f"Override: {self.override_file}")
        print(f"Faltantes: {self.missing_file} ({len(missing)}{' -- incluye lo todavia no hasheado' if partial else ''})")


if __name__ == "__main__":
    assert _ra_hash(b"x" * 8192) == hashlib.md5(b"x" * 8192).hexdigest()
    headered = b"h" * 512 + b"x" * 8192
    assert _ra_hash(headered) == hashlib.md5(b"x" * 8192).hexdigest()
    print("source_resync smoke check: OK")
