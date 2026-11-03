# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Python tool to find download URLs for RetroAchievements-compatible ROMs on archive.org, given a RetroAchievements hash. Two independent front ends share the same underlying JSON dataset but **do not share code**:

- **Console app** (`main.py`, `Console_mode.py`, `want_to_play.py`) — layered OOP app under `src/`.
- **Web app** (`api/index.py`) — a single-file Flask app, deployed to Vercel via `vercel.json` (routes everything to `api/index.py`). Templates in `api/templates/`, static assets in `api/static/`.

## Commands

```bash
pip install -r requirements.txt

python main.py            # unified console entry point, prompts for mode
python Console_mode.py    # direct hash search only (no credentials needed)
python want_to_play.py    # "want to play" list mode (needs .env, see below)

python api/index.py       # run the Flask web app locally (debug=True)
```

No test suite, linter, or type-checker config exists in this repo.

`.env` (copy from `ejemplo.env`) is only required for the "want to play" mode: `API_KEY` and `RETROACHIEVEMENTS_USERNAME` for the RetroAchievements Web API. Direct hash search needs no credentials.

## Architecture — console app (`src/`)

Classic Strategy / Factory / Command / Singleton split:

- `src/app.py` — `RetroAchievementsDownloader`, picks a `HashSearchStrategy` based on `AppMode` (`DIRECT_HASH` / `WANT_TO_PLAY`) and drives the run loop.
- `src/core/data_manager.py` — `RetroAchievementsDataManager` is a **singleton** that lazily loads `Data/TamperMonkeyRetroachievements.json` once per process and exposes `find_hash(hash) -> rom_path`.
- `src/strategies/search_strategies.py`:
  - `DirectHashSearchStrategy` — looks up a hash directly, infers console name from substrings in `rom_path`.
  - `WantToPlaySearchStrategy` — reads `game_hashes.json` (gitignored, user-generated), picks the best hash per game by region priority (`config.PREFERRED_REGIONS`: ES > USA > WORLD > EUROPE > JPN), then resolves that hash through the same `RetroAchievementsDataManager`.
- `src/factories/url_factory.py` — `URLGeneratorFactory` holds an ordered list of `URLGenerator`s (SNES, NES, PSP, PS1, PS2, Sega, Arcade, Default-fallback) and picks the first whose `can_handle(rom_path)` matches. Order matters: more specific generators (e.g. PSP, PS2) must precede broader ones (PS1, Default) since matching is substring-based. PS2 additionally splits into A-M / N-Z archive.org collections based on the first letter of the ROM filename.
- `src/commands/download_commands.py` — `OpenInBrowserCommand` (opens the generated URL), `BatchDownloadCommand` (opens many, writes unresolved names to `missing_games.txt`), `DisplayURLCommand` (print only).
- `config.py` — single source of truth for file paths, region priority, per-console base URLs, validation constants. Consumed via `import config` with `try/except ImportError` fallbacks scattered through `src/core` and `src/strategies`.

## Architecture — web app (`api/index.py`)

Self-contained Flask app that **reimplements** the hash lookup and URL-generation logic from `src/` as module-level functions instead of importing `src/` or `config.py`:

- `load_json_file()` caches `Data/TamperMonkeyRetroachievements.json` in a global; `build_games_index()` caches a derived per-game index (name, consoles, version count) for the `/games` and `/api/games` listing/filter endpoints.
- `get_console_from_rom_path()` maps raw root-folder names to canonical console labels via an alias table (handles abbreviations/typos like `megadriv`, `npg`).
- `get_download_url()` duplicates `URLGeneratorFactory`'s branching (SNES/NES/Arcade/PSP/PS2 A-M vs N-Z/PS1/default) using local `_normalize_slashes` / `_encode_rel_path` / `_strip_first_segment_if_matches` helpers that mirror `src/factories/url_factory.py` byte-for-byte in intent.
- Routes: `/` (home), `/games` + `/api/games` (paginated/filterable listing), `/dl?hash=` (redirects straight to the resolved download URL), `/get_game_versions`, `/search_games`, `/search` (JSON endpoints used by the frontend JS), `/faq`.

**Consistency hazard:** any change to region/console detection, path normalization, or per-console base URLs must be made in both `src/factories/url_factory.py` (+ `config.py`) and `api/index.py`'s `get_download_url` / `get_console_from_rom_path` — they are not shared and will silently drift otherwise.

## Data

`Data/TamperMonkeyRetroachievements.json` is the canonical dataset: `{ game_id: [ { HASH: rom_path, ... }, ... ], ... }`. `rom_path`'s root folder encodes the console (e.g. `SNES-Super Famicom/...`, `PlayStation 2/...`); this convention is what both `src/` and `api/index.py` parse against instead of an explicit console field.

## Workflow

- Rama de integración: `dev`. Las ramas de trabajo salen de `dev` y hacen PR hacia `dev` (no a `main`). `main` se actualiza solo cuando se corta un release con las mejoras ya probadas en `dev`.
- Mensajes de commit en formato Conventional Commits: `tipo(scope): descripción` (`fix`, `feat`, `refactor`, `docs`, etc).

## Gotchas de Vercel (ya resueltos, pero quedan para no repetirlos)

- **`vercel.json` → `config.includeFiles` debe ser un string (glob), nunca un array.** Un array pasa la validación local pero Vercel lo rechaza silenciosamente y cae a un build "zero-config" que falla en <1s sin log útil. Hoy está en `"**"` (incluye todo el repo en el bundle de `api/index.py`, que ahora importa de `src/`).
- **El proyecto en Vercel (dashboard → Project Settings) tenía `Node.js Version: 20.x`**, descontinuado — rompía el build antes de llegar siquiera a la parte de Python. Se subió a `24.x` vía `vercel project update retroachievements --node-version 24.x --scope pipetboys-projects`.
- **Existía un `api/requirements.txt` corrupto (UTF-16, de un commit viejo "Fixes #1")** que el builder de Python prioriza sobre el `requirements.txt` de la raíz cuando ambos existen. Se borró — la raíz es la única fuente de verdad de dependencias.
- Para depurar un deploy fallido: `gh pr checks <n>` para ver si Vercel falló, luego `vercel inspect <deployment-url-o-dpl_id> --logs --scope pipetboys-projects` para el log real (requiere `vercel link` una vez por máquina).

## Working log

Running notes on in-progress/planned work on this repo. Add an entry when starting non-trivial work; mark it done (or drop it) when finished.

- **Hecho**: consolidar lógica duplicada de consola/nombre/URL entre `src/` y `api/index.py` en `src/core/rom_info.py` (PR #13 → `dev`). Ver commits `21c6e39`, `83c8fdf`, `55a84fa`.
- **Pendiente / ideas del usuario para más adelante** (sin decidir stack todavía): verificación de un hash insertado por el usuario, integración con la API de RetroAchievements para traer metadata de juegos, chequeo de compatibilidad contra sitios de terceros (ej. CoolROMs). Cuando se arranque esto, evaluar backend Python + frontend TS (Next.js zero-config con funciones Python en `api/*.py`, o "Vercel Services" si se necesitan servicios separados) — no crear la estructura de monorepo hasta que haya código TS real que la justifique.
