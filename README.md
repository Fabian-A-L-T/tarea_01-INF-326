# tarea_01 INF-326
# Instalación de Plugin
```
docker plugin install grafana/loki-docker-driver:2.9.2 --alias loki --grant-all-permissions
```
# Ejecución
Se deben ejecutar los siguentes comandos para crear los contenedores de nanoservicios, loki, promtail y grafana. Esto se hace dentro de la carpeta `tarea_01`
```
docker network create tarea_01
docker-compose up -d
```
