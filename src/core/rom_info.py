"""
Utilidades de dominio para interpretar rom_path: consola, nombre de juego y
metadata de región/hack/traducción. Usado tanto por la app de consola como
por la web (api/index.py), para no duplicar esta lógica en los dos lados.
"""


def get_console_from_rom_path(rom_path: str) -> str:
    """Devuelve el nombre canónico de consola a partir de la carpeta raíz.
    Unifica alias, abreviaturas y variaciones (p.ej. nes/NES, megadriv -> Genesis/Mega Drive, npg -> Neo Geo Pocket).
    """
    norm = rom_path.replace('\\', '/').strip()
    root = norm.split('/', 1)[0] if '/' in norm else norm
    raw = root.strip()

    # Normalización básica del texto del root
    t = raw.lower()
    for ch in ['_', '-', '&', '(', ')', '[', ']', ',', '.']:
        t = t.replace(ch, ' ')
    t = ' '.join(t.split())  # compactar espacios

    # Mapa de alias -> nombre canónico
    aliases = {
        # Arcade
        'arcade': 'ARCADE',

        # Nintendo
        'snes': 'SNES',
        'snes super famicom': 'SNES',
        'super nintendo': 'SNES',
        'nes': 'NES',
        'nes famicom': 'NES',
        'nintendo 64': 'N64',
        'n64': 'N64',
        'nintendo ds': 'Nintendo DS',
        'nds': 'Nintendo DS',
        'game boy': 'Game Boy',
        'gb': 'Game Boy',
        'game boy color': 'Game Boy Color',
        'gbc': 'Game Boy Color',
        'game boy advance': 'Game Boy Advance',
        'gba': 'Game Boy Advance',

        # Sega
        'genesis': 'Genesis/Mega Drive',
        'mega drive': 'Genesis/Mega Drive',
        'megadrive': 'Genesis/Mega Drive',
        'megadriv': 'Genesis/Mega Drive',
        'md': 'Genesis/Mega Drive',
        'genesis mega drive': 'Genesis/Mega Drive',
        'mega drive genesis': 'Genesis/Mega Drive',
        'sega master system': 'Master System',
        'master system': 'Master System',
        'sms': 'Master System',
        'game gear': 'Game Gear',
        'gg': 'Game Gear',
        'sega cd': 'Sega CD',
        'sega 32x': 'Sega 32X',
        '32x': 'Sega 32X',
        'dreamcast': 'Dreamcast',
        'dc': 'Dreamcast',

        # PlayStation
        'playstation': 'PS1',
        'psx': 'PS1',
        'ps1': 'PS1',
        'playstation 2': 'PS2',
        'ps2': 'PS2',
        'playstation portable': 'PSP',
        'psp': 'PSP',

        # NEC / PC Engine family
        'pc engine': 'PC Engine',
        'pcengine': 'PC Engine',
        'pce': 'PC Engine',
        'turbo grafx 16': 'TurboGrafx-16',
        'turbografx 16': 'TurboGrafx-16',
        'tg16': 'TurboGrafx-16',
        'supergrafx': 'SuperGrafx',
        'super grafx': 'SuperGrafx',

        # SNK Neo Geo Pocket
        'neo geo pocket': 'Neo Geo Pocket',
        'npg': 'Neo Geo Pocket',  # posible typo invertido
        'ngp': 'Neo Geo Pocket',
        'neo geo pocket color': 'Neo Geo Pocket Color',
        'ngpc': 'Neo Geo Pocket Color',

        # Atari
        'atari 2600': 'Atari 2600',
        'atari 7800': 'Atari 7800',
        'atari lynx': 'Atari Lynx',
        'atari jaguar': 'Atari Jaguar',

        # MSX
        'msx': 'MSX',
        'msx2': 'MSX2',

        # WonderSwan
        'wonderswan': 'WonderSwan',
        'ws': 'WonderSwan',
        'wonderswan color': 'WonderSwan Color',
        'wsc': 'WonderSwan Color',

        # Otros
        '3do': '3DO',
        'amiga': 'Amiga',
        'amiga cd32': 'Amiga CD32',
        # Sega SG-1000
        'sg 1000': 'SG-1000',
        'sg1000': 'SG-1000',
        'sg': 'SG-1000',  # solo si raíz es exactamente "sg", poco probable pero inofensivo
        'sega 1000': 'SG-1000',
        'sega1000': 'SG-1000',
    }

    # Devolver mapeo canónico si existe, si no, devolver la raíz original "bonita"
    if t in aliases:
        return aliases[t]

    # Como fallback, capitalizar palabras (evita duplicados por mayúsculas/minúsculas)
    pretty = ' '.join(w.capitalize() for w in t.split()) if t else raw
    return pretty or raw


def extract_game_name(rom_path: str) -> str:
    """Extrae el nombre del juego de un rom_path.

    Usa la carpeta inmediatamente anterior al archivo; si no es válida
    (p.ej. '!_flycast' o la carpeta raíz de la consola), usa el nombre del
    archivo sin extensión.
    """
    path = rom_path.replace('\\', '/').strip()
    parts = [p for p in path.split('/') if p]
    if not parts:
        return rom_path
    filename = parts[-1]
    root = parts[0]
    folder = parts[-2] if len(parts) >= 2 else ''

    def clean(name: str) -> str:
        # Quitar extensión y normalizar espacios/guiones bajos
        base = name.rsplit('.', 1)[0]
        base = base.replace('_', ' ').strip()
        # Compactar múltiples espacios
        return ' '.join(base.split())

    invalid_folder_names = {root.lower(), 'arcade'}
    is_invalid = (not folder) or folder.lower() in invalid_folder_names or folder.startswith('!_')
    candidate = folder if not is_invalid else clean(filename)
    return candidate


def analyze_rom_info(rom_path: str) -> dict:
    """Extrae región y flags de hack/traducción/original del nombre de archivo,
    con una prioridad de selección (menor número = mayor prioridad)."""
    parts = rom_path.split('/')
    filename = parts[-1] if parts else rom_path

    is_hack = "[Hack]" in filename
    is_translation = "[T+" in filename
    is_original = "[!]" in filename

    region = "Unknown"
    if "(U)" in filename:
        region = "USA"
    elif "(E)" in filename:
        region = "Europe"
    elif "(J)" in filename:
        region = "Japan"
    elif "(UE)" in filename:
        region = "USA/Europe"

    if is_original and not is_hack and not is_translation:
        priority = 1  # ROMs originales tienen máxima prioridad
    elif is_original and is_translation:
        priority = 2  # Traducciones oficiales
    elif is_hack:
        priority = 3  # Hacks tienen menor prioridad
    else:
        priority = 4  # Otros

    return {
        'filename': filename,
        'region': region,
        'is_hack': is_hack,
        'is_translation': is_translation,
        'is_original': is_original,
        'priority': priority
    }


if __name__ == "__main__":
    assert get_console_from_rom_path("SNES-Super Famicom/Game (U).sfc") == "SNES"
    assert get_console_from_rom_path("PlayStation 2/A-M/Foo (U).iso") == "PS2"
    assert get_console_from_rom_path("arcade/!_flycast/foo.zip") == "ARCADE"
    assert get_console_from_rom_path("megadriv/Sonic (U).bin") == "Genesis/Mega Drive"
    assert get_console_from_rom_path("npg/Some Game (J).ngp") == "Neo Geo Pocket"

    assert extract_game_name("SNES-Super Famicom/Super Mario World (U).sfc") == "Super Mario World (U)"
    assert extract_game_name("arcade/!_flycast/sfiii3_usa.zip") == "sfiii3 usa"
    assert extract_game_name("arcade/arcade/pacman.zip") == "pacman"

    info = analyze_rom_info("PlayStation/Foo [Hack].bin")
    assert info['is_hack'] is True and info['priority'] == 3

    print("rom_info smoke check: OK")
