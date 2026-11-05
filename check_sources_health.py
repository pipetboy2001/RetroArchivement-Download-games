"""
Chequea si las fuentes de descarga siguen vivas: por cada consola, prueba
una muestra al azar de ROMs contra la URL real que generaria la app. Si
una consola cae por debajo del umbral, se asume que la fuente murio (no es
ruido de 1-2 archivos sueltos rotos).

Uso:
    python check_sources_health.py [--sample-size 15] [--threshold 0.5]

Escribe el reporte en sources_health_report.md y sale con status 1 si
alguna consola quedo por debajo del umbral (asi el workflow de GitHub
Actions se entera y dispara la alerta).
"""
import argparse

from src.core.source_health import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-size", type=int, default=15, help="ROMs a probar por consola")
    parser.add_argument("--threshold", type=float, default=0.5, help="Fraccion minima alcanzable antes de marcar la consola como rota")
    args = parser.parse_args()

    report, any_broken = run(args.sample_size, args.threshold)
    print(report)

    with open("sources_health_report.md", "w", encoding="utf-8") as f:
        f.write(report + "\n")

    if any_broken:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
