"""
Modo consola - Búsqueda directa por hash.
Interfaz de línea de comandos para buscar ROMs por hash.
"""

from src.app import create_direct_hash_app


def main():
    """Función principal para el modo consola."""
    app = create_direct_hash_app()
    app.run()


if __name__ == "__main__":
    main()
