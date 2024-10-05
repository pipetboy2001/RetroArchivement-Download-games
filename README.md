# RetroAchievements Downloader

Este proyecto permite buscar y descargar juegos de **RetroAchievements** a partir de sus hashes utilizando un script en Python. El script se basa en el archivo JSON disponible en [archive.org](https://archive.org/download/retroachievements_collection_v5).

## Tabla de Contenidos
- [RetroAchievements Downloader](#retroachievements-downloader)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Cómo utilizar](#cómo-utilizar)
  - [Requisitos](#requisitos)
  - [Agradecimientos](#agradecimientos)
  - [Contribuciones](#contribuciones)

## Cómo utilizar

1. **Clona este repositorio** o descarga los archivos en tu máquina local:

   ```bash
   git clone https://github.com/pipetboy2001/RetroArchivement-Download-games.git
   cd RetroArchivement-Download-games` 

2.  **Instala las dependencias necesarias**. Puedes hacerlo de dos maneras:
    
    2.1. **Manualmente** utilizando `pip`:
    
    `pip install requests rich` 
    
    2.2. **Usando el script batch**: Haz doble clic en `run_script.bat`. Esto verificará las dependencias y las instalará automáticamente si es necesario.
    
3.  **Ejecuta el script**. Puedes hacerlo de dos formas:
    
    -   **Usando el script batch**: Haz doble clic en `run_script.bat`, que ejecutará automáticamente el script de Python.
        
    -   **Usando la terminal**:
        
        `python descargar_juego.py` 
        
4.  **Introduce el hash del juego** cuando se te solicite lo podras encontrar en el apartado de Supported Game File del juego que buscas. El script buscará el hash en el archivo JSON y abrirá la URL de descarga en tu navegador si se encuentra.
    

## Requisitos

-   **Python 3.x**: Asegúrate de tener instalada una versión compatible de Python.
-   Las bibliotecas necesarias se instalarán automáticamente o puedes instalarlas manualmente como se indica arriba.

## Agradecimientos

Este proyecto está basado en el script que utiliza el archivo JSON de **RetroAchievements** disponible en [archive.org](https://archive.org/download/retroachievements_collection_v5).

## Contribuciones

Si deseas contribuir a este proyecto, por favor realiza un fork del repositorio y envía un pull request con tus cambios. ¡Todas las contribuciones son bienvenidas!

----------

Si necesitas más ayuda o tienes otras solicitudes, ¡no dudes en preguntar!