"""
Resincroniza la fuente de descarga de una consola contra un item nuevo de
archive.org (cuando el item viejo murio). Genera Data/<label>_source_override.json
y Data/<label>_missing_sources.txt.

Uso:
    python sync_source.py --console SNES --item retroachievementscompatibleromsSNES
    python sync_source.py --console "TurboGrafx-16,PC Engine" --item nec-pc-engine-roms-for-retroachievements --label pcengine --header-modulus 131072
"""
import argparse

from src.core.source_resync import SourceResync


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--console", required=True, help="Consola(s) tal como las devuelve get_console_from_rom_path, separadas por coma si son varias (ej: SNES, o 'TurboGrafx-16,PC Engine')")
    parser.add_argument("--item", required=True, help="Identificador del item de archive.org (ej: retroachievementscompatibleromsSNES)")
    parser.add_argument("--label", default=None, help="Nombre para los archivos de salida (Data/<label>_source_override.json). Por defecto, la primera consola.")
    parser.add_argument("--header-modulus", type=int, default=8192, help="Modulo para la regla de header-stripping de RA (8192 para SNES, 131072 para PC Engine/TurboGrafx-16/SuperGrafx cartucho)")
    args = parser.parse_args()

    SourceResync(console=args.console, item=args.item, label=args.label, header_modulus=args.header_modulus).run()


if __name__ == "__main__":
    main()
