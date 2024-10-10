
# RetroAchievements Downloader

Este proyecto permite buscar y descargar juegos de **RetroAchievements** a partir de sus hashes utilizando tanto una **aplicación web** como un **script en Python**. Ambos se basan en el archivo JSON disponible en [archive.org](https://archive.org/download/retroachievements_collection_v5).

## Tabla de Contenidos

-   [RetroAchievements Downloader](#retroachievements-downloader)
    -   [Tabla de Contenidos](#tabla-de-contenidos)
    -   [Versiones](#versiones)
    -   [Cómo utilizar](#c%C3%B3mo-utilizar)
    -   [Requisitos](#requisitos)
    -   [Agradecimientos](#agradecimientos)
    -   [Contribuciones](#contribuciones)

## Versiones

### Versión Web

-   La versión web está disponible en: [RetroAchievements Downloader](https://retroachievements.vercel.app/).
-   Permite introducir el hash del juego directamente en un campo de búsqueda y descargarlo de forma rápida y sencilla.

### Versión de Consola

-   Para aquellos que prefieren usar la terminal, el script en Python sigue estando disponible y funciona de la misma manera.
-   [Ultima versión](https://github.com/pipetboy2001/RetroArchivement-Download-games/releases)

## Cómo utilizar

### Versión Web

1.  **Accede a la web**: Visita [RetroAchievements Downloader](https://retroachievements.vercel.app/).
2.  **Introduce el hash**: Ingresas el hash del juego en el campo correspondiente.
3.  **Descarga**: Si el hash es encontrado, el juego se descargará directamente.

### Versión de Consola

-   **Descarga la última versión** desde la sección de releases del repositorio: [Releases](https://github.com/pipetboy2001/RetroArchivement-Download-games/releases).
    
-   **Descomprime el archivo** y accede a la carpeta donde está el script `descargar_juego.py`.
    
-   **Ejecuta el script**:
    
    -   Abre una terminal en la carpeta descomprimida.
        
    -   Ejecuta el siguiente comando:
        
        `python descargar_juego.py` 
        
-   **Introduce el hash del juego** cuando se te solicite. Lo podrás encontrar en el apartado de "Supported Game File" del juego que buscas. El script buscará el hash en el archivo JSON y abrirá la URL de descarga en tu navegador si se encuentra.
    

## Requisitos

-   **Python 3.x**: Asegúrate de tener instalada una versión compatible de Python.
-   Las bibliotecas necesarias se instalarán automáticamente o puedes instalarlas manualmente como se indica arriba.

## Agradecimientos

Este proyecto está basado en el script que utiliza el archivo JSON de **RetroAchievements** disponible en [archive.org](https://archive.org/download/retroachievements_collection_v5).

## Contribuciones

Este proyecto es de código abierto y cualquier contribución es bienvenida. Si deseas participar, realiza un fork del repositorio y envía un pull request con tus cambios. Ya sea que quieras mejorar la versión web, optimizar el script en consola, o solucionar el problema de descarga del JSON, ¡toda ayuda es apreciada!
