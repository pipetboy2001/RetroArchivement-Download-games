"""
Modo lista de deseos - Want to Play.
Interfaz para descargar juegos desde tu lista de deseos.
"""

from src.app import create_want_to_play_app


def main():
    """Función principal para el modo lista de deseos."""
    app = create_want_to_play_app()
    app.run()


if __name__ == "__main__":
    main()
