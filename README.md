```Universidad San Francisco de Quito
Data Mining
Proyecto 04
John Ochoa Abad 345743

#Github Link:
https://github.com/johnnyredwood/PSET4_NYTAXIS_ML_SCRATCH_SCIKIT

#Descripción del proyecto:
Implementé una infraestructura analítica completa utilizando Docker Compose que integra Jupyter+Spark con Postgres para procesar el dataset 
NYC TLC Trips 2015-2025. El proyecto replica el proceso de ingesta de datos Parquet de taxis Yellow y Green hacia un esquema raw en Snowflake, 
construyendo posteriormente una tabla analítica unificada (One Big Table) en el esquema analytics con un único comando a través del uso de un script
de Python

Con los datos en analytics genere la limpieza y preparación de los mismos para posterior aplicación de algoritmos de ML orientados a predecir el total_amount
de pago para el pickup acorde a variables dadas por los datos. Estas predicciones se basan en modelos from Scratch y de Scikit Learn de Stochastic Gradient Descent,
Lasso, Ridge y ElasticNet afinados para los mejores parámetros a través de Grid Search. Una vez generados los modelos se genero una comparación de los mismos 
a manera de seleccionar el mejor modelo para la predicción adecuada del precio.

#Checklist de aceptación
[x] Docker Compose levanta Spark y Jupyter Notebook.
[x] Todas las credenciales/parámetros provienen de variables de ambiente (.env).
[x] Cobertura 2015–2025 (Yellow/Green) cargada en raw con matriz y conteos por lote.
[x] analytics.obt_trips creada con columnas mínimas, derivadas y metadatos.
[x] Modelos ML Scratch vs ScikitLearn
[x] README claro: pasos, variables, esquema, decisiones, troubleshooting.

#Variables de ambiente: listado y propósito; guía para .env.

Para la ejecución de los notebooks se definieron las siguientes variables de ambiente de Snowflake:

SOURCE_PATH=https://d37ci6vzurychx.cloudfront.net
YEARS=2020,2021,2022,2023,2024,2025
MONTHS=1,2,3,4,5,6,7,8,9,10,11,12
SERVICES=yellow,green
JUPYTER_TOKEN=token123
PYSPARK_PYTHON=python3
SPARK_LOCAL_IP=0.0.0.0
PORT_JUPYTER=8888
PORT_SPARK=4040
PORT_POSTGRES=5432
PORT_WAREHOUSEUI=8080
POSTGRES_HOST=postgres
POSTGRES_DB=database123
POSTGRES_USER=usuario123
POSTGRES_PASSWORD=clave123
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=adminPassword123
PG_USER=usuario_pg123
PG_DB=database123

Con estas variables siguiendo el ejemplo del .env.example incluido en el proyecto se puede reproducir el mismo con credenciales propias
de esta manera se gestiona correctamente los datos sensibles.

#Arquitectura (diagrama/tabla): Spark/Jupyter → Snowflake (raw → analytics.obt_trips).

 Loaders Raw - Taxi Trips y Zones
        │
        ▼
 Construcción OBT- Analytics
        │
        ▼
 Preparación de Datos
        │
        ▼
 Modelos ML Scratch
        │
        ▼
 Modelos ML Scikit Learn
        │
        ▼
 Comparación Modelos


#Pasos para Docker Compose y ejecución de notebooks (incluido comando para construir OBT).

Prerrequisitos
*Docker instalado
*Docker Compose instalado
*Archivo .env configurado con las credenciales de Snowflake

1. Descargar de repositorio y Configuración del Ambiente

- Descargar el repositorio a su entorno local con
git clone https://github.com/johnnyredwood/PSET4_NYTAXIS_ML_SCRATCH_SCIKIT

Crear archivo de variables de ambiente:

- Copiar el template y configurar con valores reales
cp .env.example .env

- Editar el archivo .env con tus credenciales
nano .env

2. Verificar estructura de directorios:

📁 drivers
📁 Evidencias
📁 init-scripts
│   └── 01-init-schemas.sql
📁 libros
│   📁 .ipynb_checkpoints
│   │   ├── 01_ingesta_parquet_raw-checkpoint.ipynb
│   │   ├── checkpointTaxisYellow-checkpoint.json
│   │   └── ml_total_amount_regression-checkpoint.ipynb
│   ├── 01_ingesta_parquet_raw.ipynb
│   ├── checkpointTaxisGreen.json
│   ├── checkpointTaxisYellow.json
│   ├── ml_total_amount_regression.ipynb
│   └── postgresql-42.2.5.jar
📁 logs
📁 scripts
│   └── build_obt.py
📁 warehouse_data
📁 warehouse_ui_data
│   ├── azurecredentialcache
│   ├── sessions
│   ├── storage
│   └── pgadmin4.db
.env
.env.example
.gitignore
docker-compose.yaml
Dockerfile.obt-builder
README.md
requirements.txt

3. Inicialización de la Infraestructura
Levantar los servicios con Docker Compose:

- Ejecutar en el directorio del proyecto el siguiente comando para levantar el contenedor con variables de entorno de .env
docker-compose --env-file .env up -d

- Verificar que el contenedor esté corriendo
docker-compose ps

4. Acceder a Jupyter Notebook:
Acceder al Jupyter Notebook del contenedor con el puerto y token indicados en su .env

URL: http://localhost:puerto
Token: [valor de JUPYTER_TOKEN en .env]

5. Ejecución Secuencial de Notebooks
Orden de ejecución obligatorio:

Notebook 01 - 01_ingesta_parquet_raw
Parámetros esperados:
- Años: 2015-2025 (configurado en .env)
- Meses: 1-12 (configurado en .env)  
- Servicios: yellow, green (configurado en .env)
Genera:
-Tabla RAW de datos de taxi por servicio en Snowflake

Construcción de tabla OBT

Teniendo los contenedores corriendo en Docker desde consola ejecutar el siguiente comando:

docker compose run obt-builder python /app/scripts/build_obt.py --year-start yearInicio --year-end yearFin --services serviciosSeparadosPorComa --run-id identificadorRun --months mesesSeparadosPorEspacio

De donde:
yearInicio es el año en formato entero desde el cual se quieren empezar a procesar los datos (verificar disponibilidad de datos de dicho año en esquema Raw)
yearFin es el año en formato entero hasta el cual se quieren procesar los datos (verificar disponibilidad de datos de dicho año en esquema Raw)
serviciosSeparadosPorComa son los servicios de los taxis en este caso aplica yellow,green
identificadorRun es un identificador que se poblara en la tabla obt se puede ingresar cualquiera que desee el usuario
mesesSeparadosPorEspacio son los meses de cada año que se deseen procesar en formato entero separados por espacios

Ejemplos de dicho comando para ejecutar son:

docker compose run obt-builder python /app/scripts/build_obt.py --year-start 2020 --year-end 2020 --services yellow,green --run-id full_load --months 3 4 5 6 7 8 9 10 11 12

docker compose run obt-builder python /app/scripts/build_obt.py --year-start 2022 --year-end 2022 --services yellow,green --run-id full_load

#Diseño de raw y OBT (columnas, derivadas, metadatos, supuestos).

*Esquema RAW
El esquema raw funciona como capa de aterrizaje donde se preservan los datos en su 
formato original con metadatos de ingesta. Se implementaron tablas particionadas por servicio 
y período para optimizar el manejo de los volúmenes de datos.

Estructura de tablas RAW:

NY_TAXI_RAW_YELLOW - Viajes de taxi amarillo RAW
NY_TAXI_RAW_GREEN - Viajes de taxi verde RAW
NY_TAXI_RAW_TAXI_ZONES - Zonas de Taxis de New York RAW

Columnas base preservadas del origen:

Datos temporales: pickup/dropoff datetime
Ubicaciones: PULocationID, DOLocationID
Métricas de viaje: trip_distance, passenger_count
Tarifas: fare_amount, tip_amount, tolls_amount, total_amount
Identificadores: VendorID, RatecodeID, payment_type

Metadatos de ingesta agregados:

run_id - Identificador único de la ejecución
source_year / source_month - Período de origen
ingested_at_utc - Timestamp de ingesta
service_type - Tipo de servicio (yellow/green)

*Esquema ANALYTICS - OBT
La OBT consolida todos los datos de viajes de taxis de New York en una tabla que junta toda 
la información necesaria validada y depurada a manera de ejecutar consultas de negocio
sobre la misma

Columnas de la OBT:

Temporales:
pickup_datetime, dropoff_datetime - Timestamps originales
pickup_date, pickup_hour - Componentes temporales
dropoff_date, dropoff_hour - Componentes temporales
trip_duration_min - Duración calculada en minutos

Ubicaciones:
pu_location_id, do_location_id - IDs originales
pu_zone, pu_borough - Nombres desnormalizados
do_zone, do_borough - Nombres desnormalizados

Servicio y Códigos:
vendor_id, vendor_name - Desnormalizado
rate_code_id, rate_code_desc - Desnormalizado
payment_type, payment_type_desc - Desnormalizado

Métricas y Tarifas:
passenger_count, trip_distance
fare_amount, extra, mta_tax, tip_amount
tolls_amount, improvement_surcharge
congestion_surcharge, airport_fee, total_amount

Metadatos:
run_id - Trazabilidad de la ejecución
ingested_at_utc - Fecha de procesamiento
source_service - Servicio de origen
source_year, source_month - Período origen

Supuestos de Diseño
Clave Natural: Se define basada en pickup_datetime, PULocationID, DOLocationID y VendorID para garantizar identificación única de viajes en merges

Estrategia de Idempotencia: Implementación de UPSERT basado en clave natural, permitiendo reingesta sin duplicados.

Manejo de Datos: Se han filtrado nulos en campos obligatorios y se ha definido validaciones lógicas para datos númericos de forma que los mismos
cumplan con rangos lógicos

#Calidad/auditoría: qué se valida y dónde se ve.

*Validación de Conectividad con Snowflake desde Spark:
Inicio sesión de Spark y posteriormente genero una conexión con Snowflake con mis credenciales y ejecuto una query simple de SELECT current_version()
esto lo valido en todos los notebooks antes de proceder con el consumo, procesamiento y/o lectura de datos

*Validación de Ingesta de datos:
En todos los notebooks he implementado logs en forma de prints y manejo de excepciones para ir monitoreando el proceso de consumo de todos los datos.
A su vez una vez los mismos se iban consumiendo ingresaba en Snowflake a verificar que las tablas aumenten en cantidad de filas y monitoreaba los datos
recien ingresados con queries simples desde Snowflake

*Validación del contenedor de docker:
Al tener spark-notebook: Jupyter+Spark desde un contenedor de docker verificaba que el mismo estuviera funcionando correctamente con el comando docker ps,
con el Docker Desktop verificando que el contenedor este arriba e ingresando a localhost con el puerto definido y verificando que pudiera ingresar
sin problema a Jupyter

*Comentarios respecto a modelos ML:

Enfoque general

Se implementaron cuatro modelos lineales regularizados desde cero (SGD, Ridge, Lasso, Elastic Net) utilizando NumPy puro, para demostrar comprensión de los algoritmos de optimización y regularización.

Cada modelo tiene su versión equivalente en scikit learn con idéntico preprocesamiento, lo que permite una comparación justa y reproducible de rendimiento y tiempo.

2. Preprocesamiento y features

Se incluyeron únicamente variables disponibles en pickup para evitar data leakage.

El pipeline común incluyó:

Imputación de valores ausentes.

Escalado (StandardScaler) obligatorio para los modelos con penalización L1/L2.

Codificación One-Hot de variables categóricas controlando cardinalidad (Top-K + “Other”).

PolynomialFeatures en variables numéricas clave (trip_distance, pickup_hour, passenger_count) para capturar interacciones no lineales.

Se mantuvieron seeds fijas y un split temporal (Train: años antiguos, Valid: intermedios, Test: recientes) para garantizar comparabilidad y reproducibilidad.

3. Modelos from-scratch

SGD implementado con descenso de gradiente estocástico y tasa de aprendizaje adaptable.

Ridge, Lasso y Elastic Net resolvieron sus penalizaciones mediante optimización iterativa tipo coordinate descent o gradiente regularizado.

Cada modelo se encapsuló con métodos .fit() y .predict() y métricas internas de convergencia.

4. Comparación con scikit-learn

Los pipelines equivalentes (SGDRegressor, Ridge, Lasso, ElasticNet) de scikit-learn se configuraron con los mismos hiperparámetros (alpha, l1_ratio, eta0, max_iter), escalador, polinomios

Se realizó búsqueda en malla (GridSearch) comparable entre ambas versiones, registrando métricas (RMSE, MAE, R cuadrado) y tiempos.

Las implementaciones propias mostraron resultados coherentes con sklearn, validando la correcta implementación matemática de los modelos.

5. Evaluación y métricas

Métricas utilizadas: RMSE y MAE como principales; R cuadrado como secundaria.

Se reportó una tabla comparativa completa con los ocho pipelines (4 propios + 4 sklearn) y análisis de estabilidad frente a alpha y l1_ratio.

El modelo ganador se seleccionó con base en menor RMSE en validación
