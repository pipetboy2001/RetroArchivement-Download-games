# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Python tool to find download URLs for RetroAchievements-compatible ROMs on archive.org, given a RetroAchievements hash. Three surfaces:

- **Console app** (`main.py`, `Console_mode.py`, `want_to_play.py`) — layered OOP app under `src/`.
- **Web backend** (`api/index.py`) — Flask, deployed to Vercel as the `api` service (`vercel.json`, Vercel Services model). Still server-renders most pages (`/`, `/faq`) from `api/templates/`, and exposes the JSON endpoints (`/api/games`, `/get_game_versions`, `/dl`) that both the legacy templates' JS and the new Next.js frontend consume.
- **Web frontend, growing** (`web/`) — Next.js/TypeScript, deployed as the `web` service. Only pages migrated so far get routed here (see `vercel.json` `rewrites`); everything else still falls through to Flask's catch-all.

## Commands

```bash
pip install -r requirements.txt
npm install              # root devDependencies (concurrently) for the dev scripts below
cd web && npm install     # Next.js deps

python main.py            # unified console entry point, prompts for mode
python Console_mode.py    # direct hash search only (no credentials needed)
python want_to_play.py    # "want to play" list mode (needs .env, see below)

npm run dev:api           # Flask alone, http://localhost:5000
npm run dev:web           # Next.js alone, http://localhost:3000 (proxies /api/*, /get_game_versions, /dl to :5000 in dev — see web/next.config.ts)
npm run dev                # both together (concurrently) — this is the real local dev loop for the web app
```

No test suite, linter, or type-checker config exists in this repo. `vercel dev` (the official way to run multi-service Vercel projects locally) does **not** work for this repo yet — Vercel Services' local dev doesn't support the Flask service (`No dev server available for service "api"`), confirmed by testing; that's why the root `package.json` + Next.js rewrite-proxy exist instead.

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
- Routes: `/` (home), `/api/games` (paginated/filterable listing JSON — consumed by `web/app/games/page.tsx`, not just legacy JS), `/dl?hash=` (redirects straight to the resolved download URL), `/get_game_versions`, `/search_games`, `/search` (JSON endpoints), `/faq`. `/games` itself is no longer a Flask route — Vercel's `services` rewrite sends it straight to the `web` (Next.js) service; see "Arquitectura — frontend TS" below.

**Consistency hazard:** any change to region/console detection, path normalization, or per-console base URLs must be made in both `src/factories/url_factory.py` (+ `config.py`) and `api/index.py`'s `get_download_url` / `get_console_from_rom_path` — they are not shared and will silently drift otherwise.

## Data

`Data/TamperMonkeyRetroachievements.json` is the canonical dataset: `{ game_id: [ { HASH: rom_path, ... }, ... ], ... }`. `rom_path`'s root folder encodes the console (e.g. `SNES-Super Famicom/...`, `PlayStation 2/...`); this convention is what both `src/` and `api/index.py` parse against instead of an explicit console field.

## Workflow

- Rama de integración: `dev`. Las ramas de trabajo salen de `dev` y hacen PR hacia `dev` (no a `main`). `main` se actualiza solo cuando se corta un release con las mejoras ya probadas en `dev`.
- Mensajes de commit en formato Conventional Commits: `tipo(scope): descripción` (`fix`, `feat`, `refactor`, `docs`, etc).

## Arquitectura — frontend TS (`web/`)

Decisión del issue #19: **Next.js** (App Router, Tailwind) para páginas migradas. Convive con el backend Flask vía **Vercel Services** (`vercel.json`): `web` y `api` son dos servicios independientes en el mismo deploy, ruteados por `rewrites` de nivel superior evaluados en orden (primer match gana) — el catch-all `/(.*) → api` va último, así que solo hace falta agregar una entrada explícita por cada página que se migre.

- **`/next-poc`**: página de prueba de la infraestructura, sin uso real.
- **`/games`** (PR #23): primera página real migrada, port 1:1 de la UI que antes vivía en `games.html`/`games.js` (ya borrados). `web/app/games/page.tsx` + `VersionsModal.tsx` hacen `fetch` directo a los mismos endpoints JSON de Flask (`/api/games`, `/get_game_versions`) — mismo origen en producción (Vercel Services), sin CORS ni env vars. El único cambio de backend que requirió: `/api/games` ahora también devuelve `consoles` (antes ese dato solo se inyectaba server-side vía Jinja en la ruta `/games`, que ya no existe).
- Próxima candidata a migrar: a definir — no hay más páginas en la cola todavía.

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
- **`vercel dev` no sirve para desarrollo local todavía** con este `services` setup: detecta bien ambos servicios (`web` Next.js, `api` Flask) pero falla con `[DEV_SERVICE_START_FAILED] No dev server available for service "api" (framework: flask)` — soporte de dev-server local para Python en `services` (Beta) todavía no existe. Por eso el `package.json` de la raíz + el rewrite-proxy de `web/next.config.ts` (ver Commands arriba): simulan el mismo-origen que Vercel da gratis en producción, corriendo Flask y Next.js como dos procesos separados.

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
- **Hecho**: [#19](https://github.com/pipetboy2001/RetroArchivement-Download-games/issues/19) decidir stack TS + probar el patrón en un deploy real de Vercel (`web/` + Vercel Services, PR #22).
- **Hecho**: migrar `/games` a Next.js, port 1:1 sin rediseño (PR #23). Ver "Arquitectura — frontend TS" arriba.
- **Hecho**: comandos de dev local `dev:api`/`dev:web`/`dev` (root `package.json` + proxy en `web/next.config.ts`), porque `vercel dev` no soporta Flask en `services` todavía.
- **Hecho**: chequeo semanal automático de salud de fuentes ([#12](https://github.com/pipetboy2001/RetroArchivement-Download-games/issues/12), la parte proactiva). `src/core/source_health.py` samplea N ROMs al azar por consola, genera su URL real vía `URLGeneratorFactory` y prueba `is_download_url_reachable`; si una consola cae bajo el umbral se asume fuente muerta (no ruido de archivos sueltos). `check_sources_health.py` es el CLI, `.github/workflows/check-sources.yml` lo corre cada lunes (gratis, repo público) y abre/actualiza un issue con label `fuente-rota` -- lo cierra solo cuando vuelve a estar todo OK. Validado contra el dataset real: detectó PC Engine, TurboGrafx-16, Fds y Gamegear rotos.
- **Hecho**: "Verificar ROM" en la web (PR #39 → `dev`), la parte de [#12](https://github.com/pipetboy2001/RetroArchivement-Download-games/issues/12) de contribuir/chequear archivos propios. `HasherModal` era un placeholder que ya prometía "hash en el navegador, sin subir el archivo" -- ahora lo hace de verdad: `web/app/(app)/raHash.ts` calcula el hash estilo RA 100% client-side (reglas verificadas contra el código fuente de rcheevos, no solo la doc -- la doc describe mal la regla de PC Engine, es `size & 512` no `% 131072`) y manda solo el hash a `/search` (ya existente, sin endpoint nuevo en Flask). Alcance: solo cartucho -- CD/disco pendiente, necesitaría `RAHasher` como subproceso del lado del servidor + infra de upload grande que hoy no existe (Vercel Functions tiene un límite de 4.5MB de body, fijo, no configurable).
- **Nota**: de paso se confirmó que `src/core/source_resync.py::_ra_hash` tiene mal la regla de PC Engine (usa `% 131072` en vez de `& 512`) -- no se tocó en esta PR (archivo no relacionado), pendiente de un fix aparte.
- **Pendiente**: rediseño de `/games` (decidido explícitamente como paso aparte, después del port 1:1 — sin fecha todavía). [#18](https://github.com/pipetboy2001/RetroArchivement-Download-games/issues/18) compatibilidad con terceros (CoolROMs, menor prioridad).
- **Pendiente**: resync de PC Engine/TurboGrafx-16 (fuente realmente muerta, 51 hashes caen al fallback viejo `retroachievements_collection_v5/{pce,tg16}/`, confirmado roto). El item `nec-pc-engine-roms-for-retroachievements` de archive.org **no sirve** -- se probó (`sync_source.py --console "TurboGrafx-16,PC Engine" --item nec-pc-engine-roms-for-retroachievements --header-modulus 131072`), dio 0/51 matches; confirmado a mano que es una revisión/dump distinta a la que reconoce RA (hash de "Bomberman '93 (USA).pce" no coincide con ninguno de nuestros dos hashes para ese juego). Falta encontrar otro item. Candidato a revisar primero: `hashlinks.json` de [RARomOnHashes](https://github.com/mentalblank/RARomOnHashes) (mapeo hash→URL ya resuelto para Myrient antes de su cierre, con algunos fallback a archive.org) -- puede ahorrar la búsqueda a ciegas.
