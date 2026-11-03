"""
Sincroniza game_hashes.json con tu lista "Want to Play" real de RetroAchievements.
Requiere API_KEY y RETROACHIEVEMENTS_USERNAME en .env (ver ejemplo.env).
"""
from src.core.want_to_play_sync import WantToPlaySync


def main():
    WantToPlaySync().run()


if __name__ == "__main__":
    main()
