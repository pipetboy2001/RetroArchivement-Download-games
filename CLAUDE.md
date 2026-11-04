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

## Arquitectura — frontend TS (`web/`)

Decisión del issue #19: cuando se migre una página real a TypeScript, es **Next.js** (App Router, Tailwind). `web/` ya existe como esqueleto mínimo probado en producción (`app/next-poc/page.tsx`), sin ninguna página real migrada todavía — no agregar features ahí hasta que haya una razón concreta (ver Working log). Convive con el backend Flask vía **Vercel Services** (`vercel.json`): `web` y `api` son dos servicios independientes en el mismo deploy, ruteados por `rewrites` de nivel superior. El catch-all de Flask (`/`, `/games`, `/dl`, `/faq`, etc.) sigue intacto; Next.js solo recibe los paths que se le asignen explícitamente (hoy, `/next-poc`).

## Gotchas de Vercel (ya resueltos, pero quedan para no repetirlos)

- **El modelo de deploy es `services`** (no el `builds`/`routes` legacy, no `experimentalServices` que ya está superado). Ejemplo mínimo funcionando:
  ```json
  {
    "services": {
      "web": { "root": "web/" },
      "api": { "root": ".", "entrypoint": "api.index:app" }
    },
    "rewrites": [
      { "source": "/next-poc(.*)", "destination": { "service": "web" } },
      { "source": "/(.*)", "destination": { "service": "api" } }
    ]
  }
  ```
- **El `entrypoint` de un servicio Python usa notación de módulo con puntos, no de filesystem.** Para `api/index.py` con `root: "."`, es `"api.index:app"` — **no** `"api/index:app"` ("path does not exist") ni `"api/index.py:app"` (lo interpreta como paquete `index/py.py`, mismo error). Es el mismo formato que el ejemplo oficial `"main:app"` para un `main.py` en la raíz del servicio, solo que acá hay que incluir el paquete (`api.`) porque el archivo no está en la raíz del servicio.
- **Con `root: "."` para el servicio Python, NO hace falta `includeFiles`**: a diferencia del builder legacy `@vercel/python` (que solo empaquetaba el directorio de la función salvo que se declarara explícitamente), Services con `root: "."` incluye todo el árbol del repo por defecto. `src/`, `config.py`, `Data/*.json` quedan disponibles sin configuración extra.
- **El proyecto en Vercel (dashboard → Project Settings) tenía `Node.js Version: 20.x`**, descontinuado — rompía el build antes de llegar siquiera a la parte de Python. Se subió a `24.x` vía `vercel project update retroachievements --node-version 24.x --scope pipetboys-projects`.
- **Existía un `api/requirements.txt` corrupto (UTF-16, de un commit viejo "Fixes #1")** que el builder de Python prioriza sobre el `requirements.txt` de la raíz cuando ambos existen. Se borró — la raíz es la única fuente de verdad de dependencias.
- Para depurar un deploy fallido: `gh pr checks <n>` para ver si Vercel falló. Para el detalle real: `vercel deploy --scope pipetboys-projects --yes` local (reproduce el error de build/schema al instante, mucho más rápido que esperar el preview de GitHub) y, para errores en runtime (ej. `FUNCTION_INVOCATION_FAILED`), `vercel logs <deployment-url> --scope pipetboys-projects` (no `vercel inspect --logs`, que solo trae logs de build).
- Las preview deployments tienen **Vercel Authentication** activado por default — `curl` directo da 401. Usar `vercel curl <url> --scope pipetboys-projects` (genera un bypass token automáticamente) para probarlas desde la terminal.

## API de RetroAchievements

- `src/core/retroachievements_api.py`: `RetroAchievementsClient`, wrapper fino sobre `requests` para la Web API de RA (`API_KEY` en `.env`). Reintenta automáticamente (3 intentos, 1s de pausa) errores de red, no de HTTP status — útil porque la API a veces se queda colgada varios segundos sin devolver ni un 429 explícito.
- `sync_want_to_play.py` → genera `game_hashes.json` (personal, gitignored) desde tu lista "Want to Play".
- `sync_games_metadata.py` → genera `Data/retroachievements_metadata.json` (público, se commitea) cruzando **todo** el catálogo por hash exacto vía `GetGameList(consoleId, h=1)` (trae todos los hashes de una consola en una sola llamada — no hace falta pedirlos juego por juego). Usado por `/games` (carátulas/logros) y por `src/core/link_checker.py` (¿RA reconoce este hash?).
- **No existe un endpoint público hash→GameID** en la Web API de RA (confirmado contra la doc oficial). Por eso `sync_games_metadata.py` matchea consolas por nombre normalizado (con una tabla chica de alias a mano para NES/SNES/PS1/PS2/PSP/N64/etc, que no matchean por nombre normalizado contra RA) y dentro de cada consola matchea por hash exacto, no por título.
- **Rate limiting real**: no hay un número publicado, pero en la práctica la API empieza a devolver timeouts de lectura (no un 429 limpio) después de un uso intenso en poco tiempo (ej. correr `sync_want_to_play.py` sobre 428 juegos y después `sync_games_metadata.py` varias veces seguidas). Si `sync_games_metadata.py` falla con `ReadTimeoutError` repetido, esperar un rato antes de reintentar — no es un bug, es la API limitándonos.
- `archive.org` devuelve **401** (no 404) para archivos que existen pero requieren login en el navegador — `link_checker.is_download_url_reachable` solo cuenta 404/410 como "roto", 401/403 cuenta como alcanzable.

## Working log

Running notes on in-progress/planned work on this repo. Add an entry when starting non-trivial work; mark it done (or drop it) when finished.

- **Hecho**: consolidar lógica duplicada de consola/nombre/URL entre `src/` y `api/index.py` en `src/core/rom_info.py` (PR #13 → `dev`).
- **Hecho**: limpiar constantes muertas de `config.py` (PR #14).
- **Hecho**: auto-generar `game_hashes.json` desde la API de RA (PR #15).
- **Hecho** (código completo, dato pendiente de generar): issues [#16](https://github.com/pipetboy2001/RetroArchivement-Download-games/issues/16) + [#17](https://github.com/pipetboy2001/RetroArchivement-Download-games/issues/17) juntas — metadata de RA en `/games` + verificación de hash/link. El código está probado (smoke checks, `/search` y `/games` funcionan sin el archivo de metadata presente, degradan a `None`/`False`), pero **`Data/retroachievements_metadata.json` todavía no se generó** porque la API de RA empezó a devolver timeouts por uso intenso durante las pruebas de hoy. Falta: correr `python sync_games_metadata.py` cuando la API esté respondiendo normal, y commitear el archivo resultante.
- **Hecho**: [#19](https://github.com/pipetboy2001/RetroArchivement-Download-games/issues/19) decidir stack TS + probar el patrón en un deploy real de Vercel (`web/` + Vercel Services). Ver sección "Arquitectura — frontend TS" arriba. No se migró ninguna página real todavía — próxima vez que se toque esto, candidato natural: `/games`.
- **Pendiente**: [#18](https://github.com/pipetboy2001/RetroArchivement-Download-games/issues/18) compatibilidad con terceros (CoolROMs, menor prioridad).
