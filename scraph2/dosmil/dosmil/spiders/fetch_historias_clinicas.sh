#!/bin/bash

# Establecer un valor predeterminado para la cantidad de historias clínicas a recuperar
COUNT=15
MODE="random"  # Modo predeterminado
LOT_SIZE=50

# Analizar opciones con getopts
while getopts ":n:res:" opt; do
  case $opt in
    n)
      COUNT=$OPTARG
      ;;
    r)
      MODE="random"
      ;;
    s)
      START=$OPTARG
      MODE="range"
      ;;
    e)
      END=$OPTARG
      MODE="range"
      ;;
    \?)
      echo "Opción inválida: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "La opción -$OPTARG requiere un argumento." >&2
      exit 1
      ;;
  esac
done

# Validar que end sea mayor que start en el modo rango
if [[ $MODE == "range" && ( -z $START || -z $END || $END -le $START ) ]]; then
    echo "En modo rango, -s (start) y -e (end) son requeridos, y end debe ser mayor que start."
    exit 1
fi

# Crear el directorio "files" si no existe
mkdir -p files

# Obtener la fecha actual en formato YYYY-MM-DD HH:MM:SS
CURRENT_DATE=$(date +"%Y-%m-%d %H:%M:%S")

if [[ $MODE == "random" ]]; then
    # Genera un número aleatorio entre 1 y 11000
    RANDOM_IDS=$(shuf -i 1-11000 -n $COUNT | tr '\n' ',')
    echo "Recuperando historia clínica con IDS: $RANDOM_IDS"

    # Ejecuta el comando scrapy con los HC_IDS generado y guarda en el directorio "files"
    scrapy crawl hc_paciente -o "files/hc_${CURRENT_DATE}.json" -a hc_id=$RANDOM_IDS
else
    for ((i=$START; i<=$END; i+=$LOT_SIZE)); do
        LOT_END=$((i+LOT_SIZE-1))
        if [ $LOT_END -gt $END ]; then
            LOT_END=$END
        fi

        HC_IDS=$(seq $i $LOT_END | tr '\n' ',')
        echo "Recuperando historias clínicas con IDs: $HC_IDS"

        # Ejecuta el comando scrapy con el rango de HC_IDS y guarda en el directorio "files"
        scrapy crawl hc_paciente -o "files/hc_${i}-${LOT_END}.json" -a hc_id=$HC_IDS
    done
fi
