
# 🎮 RetroAchievements Downloader  Want-to-Play

## 📝 Descripción  

**RetroAchievements Downloader** es un conjunto de scripts en **Python** que facilitan la descarga de ROMs compatibles con los logros de **RetroAchievements** 🏆.  

📌 Permite buscar juegos en tu lista de **"Want to Play"**, obtener los **hashes** y generar automáticamente la **URL de descarga** para múltiples plataformas. También puedes seleccionar juegos y consolas desde una base de datos **JSON**.  

## 🚀 Características principales  

✅ Descarga y procesamiento de archivos **JSON** con hashes de juegos.  
✅ Búsqueda eficiente de **ROMs** en un archivo local o desde la web.  
✅ Generación automática de **URLs de descarga** 🔗.  
✅ Soporte para múltiples plataformas: **SNES, NES, PSP, PS1, PS2, Dreamcast** y más.  
✅ Interfaz sencilla para **seleccionar consola y juego** antes de la descarga.  

## 📌 Requisitos  

Antes de ejecutar el proyecto, asegúrate de tener instalado lo siguiente:  

🔹 **Python 3.x** 🐍  
🔹 Módulos necesarios:  

```sh
pip install requests rich
```

## 📂 Estructura del Proyecto

```
`📁 Want to Play/
 ├── 📜 Descargar.py                 # Script principal
 ├── 📜 Intermedio.py                 # Procesa la información
 ├── 📜 ObtenerJsonConHash.py         # Genera el archivo JSON con hashes
 ├── 📜 README.md                     # Documentación del proyecto
 ├── 📜 TamperMonkeyRetroachievements.json  # JSON con los hashes
 ├── 🔒 .env                           # Variables de entorno (API Key y Username)` 
```
## 📜 Descripción de los Archivos

🔹 **`Descargar.py`** → Descarga los datos necesarios para obtener los hashes de los juegos.  
🔹 **`Intermedio.py`** → Procesa los datos descargados y los organiza.  
🔹 **`ObtenerJsonConHash.py`** → Genera un **archivo JSON** con los hashes de los juegos obtenidos.  
🔹 **`TamperMonkeyRetroachievements.json`** → Almacena los hashes extraídos.  
🔹 **`.env`** → Contiene la **API Key** y el **nombre de usuario**.

## 🔑 Configuración del archivo `.env`

Guarda tus credenciales en el archivo `.env`:

`API_KEY` : para mas informacion como obtenerla ingresa [aqui](https://api-docs.retroachievements.org/getting-started.html#get-your-web-api-key)
`USERNAME`:  nombre de usuario de RetroArchivements

## ▶️ Uso

1️⃣ Ejecutar `ObtenerJsonConHash.py` para generar el JSON de juegos con hash.  
2️⃣ Ejecutar `Intermedio.py` para procesar la información.  
3️⃣ Ejecutar `Descargar.py` para obtener los datos y generar las URLs de descarga.

✅ ¡Listo! Ahora tendrás los **hashes almacenados** en `TamperMonkeyRetroachievements.json` y listos para su uso. 🎉