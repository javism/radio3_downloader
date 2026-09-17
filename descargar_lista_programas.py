import os
import re
import json
import html
import sys
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def limpiar_nombre_archivo(nombre: str) -> str:
    """Sanea el título para que sea un nombre de archivo/directorio válido en Linux."""
    nombre_limpio = re.sub(r'[\\/*?:"<>|]', '', nombre)
    return nombre_limpio.strip()

def extraer_fecha_yyyy_mm_dd(url_media: str) -> str:
    """
    Busca el patrón DD-MM-YY en la URL y lo convierte a YYYY-MM-DD.
    Ejemplo: '...-04-09-26/...' -> '2026-09-04'
    """
    match = re.search(r'-(\d{2})-(\d{2})-(\d{2})/\d+/?$', url_media)
    if match:
        dia, mes, ano = match.groups()
        return f"20{ano}-{mes}-{dia}"
    return ""

def extraer_nombre_programa(url_programa: str) -> str:
    """Extrae el nombre del programa después de /audios/ en la URL."""
    match = re.search(r'/audios/([^/]+)', url_programa)
    if match:
        return match.group(1)
    return "programa_desconocido"

def descargar_programa(url_programa: str):
    slug_programa = extraer_nombre_programa(url_programa)
    carpeta_destino = limpiar_nombre_archivo(slug_programa)

    # Crear la carpeta del programa si no existe
    os.makedirs(carpeta_destino, exist_ok=True)

    print(f"\n==================================================")
    print(f"Procesando: {slug_programa}")
    print(f"Carpeta destino: ./{carpeta_destino}/")
    print(f"URL: {url_programa}")
    print(f"==================================================\n")

    response = requests.get(url_programa, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error al acceder a {url_programa} (Código {response.status_code})")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    elementos = soup.find_all('span', class_=re.compile(r'\btres_botones\b'))
    print(f"Se encontraron {len(elementos)} episodios disponibles.")

    descargados = 0
    for elem in elementos:
        data_share_raw = elem.get('data-share')
        if not data_share_raw:
            continue

        try:
            data_share_json = html.unescape(data_share_raw)
            metadata = json.loads(data_share_json)
            
            titulo_original = metadata.get('contentTitle')
            mp3_url = metadata.get('file')

            if not titulo_original or not mp3_url:
                continue

            # Buscar la fecha en la URL de goto_media
            prefijo_fecha = ""
            contenedor = elem.find_parent(['article', 'li', 'div'])
            if contenedor:
                enlace_goto = contenedor.find('a', class_='goto_media')
                if enlace_goto and enlace_goto.get('href'):
                    prefijo_fecha = extraer_fecha_yyyy_mm_dd(enlace_goto['href'])

            # Construir el nombre y la ruta del archivo dentro de la carpeta del programa
            titulo_limpio = limpiar_nombre_archivo(titulo_original)
            if prefijo_fecha:
                nombre_fichero = f"{prefijo_fecha}-{titulo_limpio}.mp3"
            else:
                nombre_fichero = f"{titulo_limpio}.mp3"

            ruta_completa = os.path.join(carpeta_destino, nombre_fichero)

            # Evitar re-descargar
            if os.path.exists(ruta_completa):
                print(f"[Omitido - Ya existe]: {ruta_completa}")
                continue

            print(f"Descargando en ./{carpeta_destino}/: {nombre_fichero}")
            
            audio_resp = requests.get(mp3_url, headers=HEADERS, stream=True)
            if audio_resp.status_code == 200:
                with open(ruta_completa, 'wb') as f:
                    for chunk in audio_resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"  ✔ Completado")
                descargados += 1
            else:
                print(f"  ✖ Error en la descarga (Status: {audio_resp.status_code})")

        except Exception as e:
            print(f"Error procesando episodio: {e}")
            continue

    print(f"\nFinalizado {slug_programa}. Nuevos descargados: {descargados}")

def procesar_archivo_urls(fichero_txt: str):
    if not os.path.exists(fichero_txt):
        print(f"Error: El archivo '{fichero_txt}' no existe.")
        return

    with open(fichero_txt, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    urls = [linea.strip() for linea in lineas if linea.strip() and not linea.startswith('#')]
    print(f"Se encontraron {len(urls)} URLs para procesar en '{fichero_txt}'.")

    for url in urls:
        descargar_programa(url)

if __name__ == '__main__':
    # Por defecto busca 'programas.txt', o acepta el archivo como argumento
    archivo_lista = sys.argv[1] if len(sys.argv) > 1 else 'programas.txt'
    procesar_archivo_urls(archivo_lista)