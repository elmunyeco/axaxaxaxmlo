#!/bin/bash

# Establecer un valor predeterminado para la cantidad de historias clínicas a recuperar
COUNT=15
RANGE_MODE=false
START=0
END=0

# Analizar opciones con getopts
while getopts ":n:rs:e:" opt; do
  case $opt in
    n)
      COUNT=$OPTARG
      ;;
    r)
      RANGE_MODE=false
      ;;
    s)
      RANGE_MODE=true
      START=$OPTARG
      ;;
    e)
      END=$OPTARG
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

# Validar que END sea mayor que START en modo rango
if $RANGE_MODE && [ $END -le $START ]; then
    echo "El valor de 'end' debe ser mayor que el de 'start'."
    exit 1
fi

# Crear el directorio "files" si no existe
mkdir -p files

# Función para ejecutar scrapy con los IDs generados
fetch_historias_clinicas() {
    IDS=$1
    FILE_NAME=$2
    echo "scapy crawl hc_paciente -o \"files/$FILE_NAME.json\" -a hc_id=$IDS"
}

# Generar y procesar IDs
if $RANGE_MODE; then
    for (( ID=$START; ID<=$END; ID+=5 )); do
        IDS=$(seq $ID $((ID+4)))
        FILE_NAME="hc_$ID-$((ID+4))"
        fetch_historias_clinicas "$IDS" "$FILE_NAME"
    done
else
    CURRENT_DATE=$(date +"%Y%m%d%H%M%S")
    for _ in $(seq 1 $((COUNT/5))); do
        IDS=$(shuf -i 1-11000 -n 5 | tr '\n' ',')
        FILE_NAME="hc_$CURRENT_DATE"
        fetch_historias_clinicas "$IDS" "$FILE_NAME"
    done
fi
