# Despliegue de Spotifice con IceGrid

## Descripción del Trabajo
Este proyecto consiste en el despliegue de la aplicación distribuida **Spotifice** (versión Hito 1 o superior) utilizando **IceGrid**, la herramienta de gestión de aplicaciones distribuidas del middleware ZeroC Ice.

El objetivo es gestionar la ejecución de los servicios en múltiples nodos, asegurando la disponibilidad y escalabilidad del sistema musical.

### Información
* **Asignatura:** Sistemas Distribuidos
* **Grado:** Ingeniería Informática
* **Curso:** 2025-2026
* **Fecha:** Noviembre 2025

### Autores
* Alberto Cortés Herranz
* Adrián Caballero Camacho

---

## Nivel de Despliegue Seleccionado
El despliegue realizado corresponde al siguiente nivel de dificultad:

-  **Nivel Básico:** Despliegue en al menos 2 nodos IceGrid.
-  **Nivel Intermedio:** Incluye lo anterior + 2 MediaServers + 2 MediaRenderers + uso de **IcePatch2** para distribución de código. Despliegue en 2 nodos lógicos independientes (VMs permitidas).
-  **Nivel Avanzado:** Todo lo anterior, desplegado sobre al menos **2 nodos físicos independientes**.

---

## Requisitos Previos
Para ejecutar este despliegue es necesario tener instalado:
* **ZeroC Ice** (Versión 3.7 o compatible).
* **Java Development Kit (JDK)** (Para los servicios base).
* **Python 3** (Si se utilizan componentes en Python).

---

## Estructura del Proyecto
El repositorio contiene los ficheros necesarios para la configuración y arranque:

* `/config`: Archivos XML de configuración de los nodos y descriptores de aplicación IceGrid.
* `/scripts`: Scripts de arranque para el Registry y los Nodos.
* `/src`: Código fuente de la aplicación (Cliente, Servidor, MediaServer, MediaRender).
* `/icepatch`: (Solo nivel Intermedio/Avanzado) Directorio para la distribución de binarios.

---

## Instrucciones de Despliegue y Puesta en Marcha 

### 1. Compilación
Antes de desplegar, asegurarse de que los binarios están generados:
```bash
# Ejemplo de compilación (ajustar según tu build system, ej: gradle, make)
./gradlew build
