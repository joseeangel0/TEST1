
# Reporte de Implementación: Pipeline de Datos ETL

**Proyecto:** Procesamiento de Datos para el Equipo de Servicios Galácticos
**Autor:** Valeria Nicol
**Fecha:** 2025-10-31

---

## 1. Resumen Ejecutivo

### Objetivo
El objetivo principal de este proyecto fue construir un pipeline de datos automatizado y robusto en la nube de AWS para ingestar, limpiar y procesar la información del personal del equipo de servicios galácticos, obtenida a través de una API externa (SWAPI).

### Solución Implementada
Se diseñó y desplegó un pipeline de datos 100% "serverless", aprovechando los servicios gestionados de AWS para garantizar escalabilidad, bajo costo y un mantenimiento mínimo. La solución extrae los datos, aplica un conjunto de reglas de negocio para su transformación y carga el resultado limpio en un formato accesible para su posterior análisis.

### Tecnologías Clave
- **AWS Lambda:** Para la extracción de datos (Extracción).
- **Amazon S3:** Como data lake para almacenar los datos en su estado crudo (`raw`) y procesado (`processed`).
- **AWS Glue:** Para la ejecución de los procesos de transformación y limpieza de datos (Transformación y Carga).
- **Amazon EventBridge:** Para la orquestación y programación automática del pipeline.

### Resultado Final
El proyecto culminó con un pipeline de ETL funcional, eficiente y completamente desplegado en AWS, capaz de convertir datos JSON crudos de una API en un archivo CSV limpio y estructurado, listo para ser consumido por equipos de análisis o inteligencia de negocio.

---

## 2. Arquitectura de la Solución

La arquitectura implementada sigue un patrón de diseño moderno, event-driven y serverless. El flujo de datos se puede visualizar en el siguiente diagrama:

*(Aquí, inserta una imagen exportada del archivo `solution_diagram.drawio` que generamos previamente)*

### Descripción de Componentes
1.  **Amazon EventBridge:** Actúa como el disparador (trigger) programado. Una regla configurada invoca la función Lambda una vez al día para iniciar el proceso.
2.  **AWS Lambda:** Su responsabilidad es la fase de **Extracción**. Se conecta a la API externa (SWAPI), maneja la paginación para obtener el conjunto de datos completo y deposita la información en formato JSON en la carpeta `raw/` del bucket S3.
3.  **Amazon S3:** Es el núcleo del almacenamiento. El bucket `instructions-67f86d4f` actúa como un data lake, separando los datos crudos y los procesados para mantener un linaje de datos claro y permitir reprocesamientos futuros si fuera necesario.
4.  **AWS Glue:** Se encarga de la fase de **Transformación y Carga**. Un job de Glue (escrito en PySpark) se activa cuando un nuevo archivo llega a la carpeta `raw/`. Este job lee el JSON, aplica todas las transformaciones requeridas y escribe el resultado final como un archivo CSV en la carpeta `processed/`.

---

## 3. Fases del Proyecto y Resolución de Incidencias

La implementación se abordó con una metodología iterativa, priorizando la validación local antes del despliegue en la nube.

### Fase 1: Prototipado y Pruebas Locales
Para acelerar el desarrollo y asegurar la lógica de negocio, se creó un entorno de prueba local. Se desarrollaron dos scripts en Python:
- Un script para simular la extracción de la API y guardar el JSON localmente.
- Un script con la librería `pandas` para replicar y validar las transformaciones de Glue. 

Este enfoque permitió depurar la lógica de forma rápida y eficiente antes de interactuar con los servicios de AWS.

### Fase 2: Despliegue y Adaptación a AWS
Una vez validada la lógica, los scripts locales se tradujeron a sus contrapartes nativas de AWS:
- El script de extracción se adaptó para usar `boto3` y escribir en S3 dentro de una función Lambda.
- El script de transformación de `pandas` se reescribió en `PySpark` para ejecutarse como un job de AWS Glue.

### Fase 3: Diagnóstico y Resolución de Incidencias
Durante el despliegue, se presentaron dos incidencias técnicas que fueron diagnosticadas y resueltas con éxito, demostrando capacidad de troubleshooting en el entorno de AWS.

1.  **Incidencia: Timeout en AWS Lambda.**
    *   **Síntoma:** La función Lambda fallaba con un error de `timeout` después de 3 segundos.
    *   **Diagnóstico:** Se determinó que el tiempo de ejecución por defecto de 3 segundos era insuficiente para completar todas las peticiones paginadas a la SWAPI.
    *   **Solución:** Se modificó la configuración de la función Lambda, aumentando el tiempo de espera a **30 segundos**, lo cual resolvió la incidencia de forma inmediata.

2.  **Incidencia: Error de Ejecución en AWS Glue.**
    *   **Síntoma:** El job de Glue fallaba y la carpeta `processed/` permanecía vacía.
    *   **Diagnóstico:** El análisis de los logs del job en **CloudWatch** reveló un `TypeError`, indicando una incorrecta invocación de método al intentar convertir un DataFrame de Spark a un DynamicFrame de Glue.
    *   **Solución:** Se corrigió el script de PySpark, ajustando la sintaxis a `DynamicFrame.fromDF(...)` y añadiendo la importación de `DynamicFrame` que faltaba. Esto alineó el código con la API correcta de AWS Glue.

---

## 4. Conclusión

Este proyecto demuestra la capacidad de diseñar, implementar y depurar un pipeline de datos de extremo a extremo en AWS. La elección de una arquitectura serverless no solo cumple con los requisitos técnicos, sino que también representa una solución moderna, rentable y altamente escalable. La metodología de pruebas locales y la resolución efectiva de incidencias en la nube validan un sólido entendimiento tanto de los principios de ingeniería de software como del ecosistema de AWS.
