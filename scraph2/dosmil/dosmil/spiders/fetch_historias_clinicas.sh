#!/bin/bash

# Establecer un valor predeterminado para la cantidad de historias clínicas a recuperar
COUNT=15

# Analizar opciones con getopts
while getopts ":n:" opt; do
  case $opt in
    n)
      COUNT=$OPTARG
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

# Crear el directorio "files" si no existe
mkdir -p files

for _ in $(seq 1 $COUNT); do
    # Genera un número aleatorio entre 1 y 11000
    HC_ID=$(shuf -i 1-11000 -n 1)
    echo "Recuperando historia clínica con ID: $HC_ID"
    
    # Ejecuta el comando scrapy con el HC_ID generado y guarda en el directorio "files"
    scrapy crawl hc_paciente -o "files/hc_${HC_ID}.json" -a hc_id=$HC_ID
done

