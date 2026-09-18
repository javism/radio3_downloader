import os
import re
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TALB, TPE1

def procesar_musica(directorio_raiz):
    # Expresión regular para capturar la fecha (yyyy-mm-dd) y el título
    patron_archivo = re.compile(r'^\d{4}-\d{2}-\d{2}-(.*)\.mp3$', re.IGNORECASE)

    for carpeta_actual, _, archivos in os.walk(directorio_raiz):
        # El nombre de la carpeta contenedora será el Álbum
        nombre_programa = os.path.basename(carpeta_actual)

        for archivo in archivos:
            coincidencia = patron_archivo.match(archivo)
            if coincidencia:
                # Extraemos solo el título eliminando la fecha
                titulo_extraido = coincidencia.group(1).strip()
                ruta_completa = os.path.join(carpeta_actual, archivo)

                try:
                    # Intentar cargar las etiquetas ID3 existentes
                    audio = ID3(ruta_completa)
                except ID3NoHeaderError:
                    # Si el archivo no tiene cabecera ID3, creamos una nueva
                    audio = ID3()

                # Asignar/Sobrescribir los metadatos requeridos
                audio["TPE1"] = TPE1(encoding=3, text="Radio 3")          # Artista / Autor
                audio["TALB"] = TALB(encoding=3, text=nombre_programa)    # Álbum (Nombre carpeta)
                audio["TIT2"] = TIT2(encoding=3, text=titulo_extraido)    # Título (Sin fecha)

                # Guardar los cambios directamente en el archivo
                audio.save(ruta_completa)
                print(f"Modificado: {archivo} -> Título: '{titulo_extraido}', Álbum: '{nombre_programa}'")

if __name__ == "__main__":
    ruta_objetivo = "./"
    
    if os.path.exists(ruta_objetivo):
        procesar_musica(ruta_objetivo)
        print("\n¡Proceso completado con éxito!")
    else:
        print("La ruta especificada no existe. ")
