# Descarga programas de Radio 3

Script para descargar los programas de Radio 3 ordenados por carpetas y fechas. 

## Dependencias

``` 
pip install beautifulsoup4 requests
``` 

## Uso 

Listar las URL de los programas a programa por línea en un fichero txt: 

```{bash} 
python3 descargar_lista_programas.py programas.txt
``` 

Estructura resultante: 

```{bash} 
.
├── descargar_lista_programas.py
├── programas.txt
├── turbo-3/
│   ├── 2026-09-04-Viernes Eléctrico... y numetalero.mp3
│   └── 2026-09-08-Lo nuevo de Anni B Sweet.mp3
└── 180-grados/
    └── 2026-09-07-Programa completo.mp3
```

