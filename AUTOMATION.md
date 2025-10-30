
# Automatización del Pipeline con Amazon EventBridge

Para ejecutar este pipeline de datos de forma automática cada día, el servicio ideal en AWS es **Amazon EventBridge**.

EventBridge es un servicio de bus de eventos "serverless" que te permite conectar tus aplicaciones con datos de una variedad de fuentes. Una de sus funciones clave es la capacidad de crear **reglas programadas** (como una tarea cron) para invocar servicios de AWS.

### Pasos para la Automatización Diaria

A continuación se describe el proceso para configurar una regla en EventBridge que ejecute la función Lambda de extracción todos los días a una hora específica.

1.  **Ir a la Consola de Amazon EventBridge:**
    *   En la consola de AWS, busca y navega al servicio "Amazon EventBridge".

2.  **Crear una Nueva Regla:**
    *   En el panel de EventBridge, haz clic en el botón "Crear regla".
    *   **Nombre y descripción:** Dale un nombre descriptivo a la regla, por ejemplo, `Daily-SWAPI-ETL-Trigger`.

3.  **Definir el Patrón de Programación (Schedule):**
    *   En la sección "Definir patrón", elige la opción **"Programación" (Schedule)**.
    *   Selecciona la opción **"Expresión cron"** para tener un control preciso. Para ejecutar la regla todos los días a las 02:00 AM (UTC), puedes usar la siguiente expresión:
        ```
        cron(0 2 * * ? *)
        ```
        *Esto significa: en el minuto 0, de la hora 2, todos los días del mes, todos los meses, cualquier día de la semana.*

4.  **Seleccionar el Objetivo (Target):**
    *   El "objetivo" es el servicio que la regla va a invocar cuando se cumpla la programación.
    *   En la sección "Seleccionar destinos", elige **"Servicio de AWS"**.
    *   En el menú desplegable, selecciona **"Función de Lambda"**.

5.  **Configurar el Objetivo:**
    *   En el desplegable "Función", selecciona la función Lambda que creaste para la extracción de datos (la que contiene el código de `lambda_function.py`).
    *   EventBridge se encargará de añadir los permisos necesarios al rol de la regla para que pueda invocar tu función Lambda.

6.  **Crear la Regla:**
    *   Haz clic en "Crear" para finalizar la configuración.

### Flujo del Proceso Automatizado

Una vez creada la regla:

1.  **Cada día a las 2:00 AM (UTC)**, Amazon EventBridge se activará.
2.  Invocará automáticamente tu función **AWS Lambda**.
3.  La función Lambda extraerá los datos de la SWAPI y los guardará en la carpeta `raw/` de S3.
4.  La llegada del nuevo archivo a S3 activará el **Job de AWS Glue** (asumiendo que se configura un disparador o "trigger" en Glue basado en eventos de S3), el cual procesará los datos y los dejará en la carpeta `processed/`.

De esta forma, el pipeline completo se ejecuta sin ninguna intervención manual.
