```Universidad San Francisco de Quito
Data Mining
Proyecto 05
John Ochoa Abad 345743

#Github Link:
https://github.com/johnnyredwood/PSET5-ENSEMBLE-REGRESSION

#Descripción del proyecto:
Infraestructura analítica completa con Docker Compose integrando Jupyter+Spark y Postgres para procesar el dataset NYC TLC Trips 2015–2025. Se ingesta cobertura Yellow y Green en esquema RAW y se construye una tabla analítica unificada (One Big Table) en el esquema `analytics` mediante un único comando (`build_obt.py`).

Sobre la OBT se realiza muestreo controlado y preparación de features (scaling numéricas + one-hot categóricas) para entrenar y comparar modelos de regresión enfocándose en predecir `total_amount` al pickup. En esta versión (PSET5) se evoluciona desde modelos lineales regularizados hacia un set de modelos ensemble (Voting, Bagging, Pasting, Gradient Boosting y LightGBM) más un baseline lineal, seleccionando el mejor por RMSE temporal en validación y auditando desempeño en test.

#Checklist de aceptación
[x] Docker Compose levanta Spark y Jupyter Notebook.
[x] Variables sensibles gestionadas vía archivo .env.
[x] Cobertura 2015–2025 (Yellow/Green) cargada en RAW con monitoreo por lote.
[x] Tabla `analytics.obt_trips` construida con columnas base, derivadas y metadatos.
[x] Muestreo controlado y particionado temporal (Train ≤2022 / Val 2023 / Test 2024).
[x] Modelos Ensemble (Voting, Bagging, Pasting, Gradient Boosting, LightGBM) comparados con baseline.
[x] Selección por menor RMSE en validación manteniendo MAE y R² estables.
[x] README claro: pasos, variables, arquitectura, decisiones y troubleshooting.

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

#Arquitectura (flujo resumido)

 Ingesta Parquet (Yellow/Green & Zones)
        │
        ▼
 Esquema RAW (tablas particionadas + metadatos)
        │
        ▼
 Construcción OBT (`analytics.obt_trips`)
        │
        ▼
 Muestreo & Preparación (limpieza, encoding, scaling)
        │
        ▼
 Entrenamiento Modelos (Baseline + Ensembles)
        │
        ▼
 Selección & Evaluación (Validación / Test)


#Pasos para Docker Compose y ejecución de notebooks (incluido comando para construir OBT).

Prerrequisitos
*Docker instalado
*Docker Compose instalado
*Archivo .env configurado con las credenciales de Snowflake

1. Descargar de repositorio y Configuración del Ambiente

- Descargar el repositorio a su entorno local con
git clone https://github.com/johnnyredwood/PSET5-ENSEMBLE-REGRESSION/

Crear archivo de variables de ambiente:

- Copiar el template y configurar con valores reales
cp .env.example .env

- Editar el archivo .env con tus credenciales
nano .env

2. Verificar estructura de directorios (vista clave):

📁 drivers                  -> Dependencias externas (drivers JDBC, etc.)
📁 Evidencias               -> Capturas / artefactos de validación y resultados
📁 init-scripts             -> SQL inicial (esquemas, permisos) para Postgres
│   └── 01-init-schemas.sql
📁 libros                   -> Notebooks de ingesta y modelado
│   📁 .ipynb_checkpoints    -> Estados intermedios automáticos
│   ├── 01_ingesta_parquet_raw.ipynb  -> Ingesta masiva RAW
│   ├── pset5_ensemble_regression.ipynb -> Entrenamiento y comparación ensembles
│   ├── checkpointTaxisGreen.json      -> Progreso ingesta Green
│   ├── checkpointTaxisYellow.json     -> Progreso ingesta Yellow
│   └── postgresql-42.2.5.jar          -> Driver JDBC Postgres
📁 logs                     -> Logs operativos / seguimiento procesos
📁 scripts                  -> Scripts utilitarios (ETL / construcción OBT)
│   └── build_obt.py        -> Construcción tabla OBT parametrizada
📁 warehouse_data           -> Data directory Postgres (persistencia física)
📁 warehouse_ui_data        -> Data de la UI (pgAdmin / sesiones)
│   ├── azurecredentialcache
│   ├── sessions
│   ├── storage
│   └── pgadmin4.db
.env                        -> Variables de entorno locales (no versionar sensibles)
.env.example                -> Plantilla de referencia para reproducir entorno
.gitignore                  -> Exclusiones de control de versión
docker-compose.yaml         -> Orquestación de servicios (Spark, Jupyter, Postgres, pgAdmin)
Dockerfile.obt-builder      -> Imagen especializada para construcción OBT
README.md                   -> Documentación del proyecto
requirements.txt            -> Dependencias Python base

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
\n+Enfoque actualizado (PSET5 - Modelos Ensemble)\n+\n+Se migró del enfoque de modelos lineales regularizados (SGD, Ridge, Lasso, ElasticNet desde cero y sklearn) hacia un conjunto de modelos ensemble y comparativos para mejorar capacidad predictiva sobre `total_amount` y robustez temporal.\n+\n+Modelos incluidos:\n+* Baseline: Regresión Lineal con preprocesamiento.\n+* VotingRegressor: combinación de `DecisionTreeRegressor`, `Ridge`, `Lasso` (voto promedio).\n+* Bagging (bootstrap) sobre árboles de decisión.\n+* Pasting (sin bootstrap) como contraste de muestreo.\n+* Gradient Boosting con búsqueda de hiperparámetros vía `GridSearchCV` + `TimeSeriesSplit`.\n+* LightGBM (`LGBMRegressor`) con grid search y control de profundidad/hojas.\n+\n+Preprocesamiento y Features:\n+* Variables únicamente disponibles al momento del pickup para evitar leakage: `passenger_count`, `trip_distance`, `pickup_hour`, `pickup_dow`, `month`, `year`, `pu_location_id`, `service_type`, `vendor_id`, `rate_code_id`, `payment_type`.\n+* Limpieza: filtrado de outliers y reglas lógicas (rango de `total_amount`, `trip_distance`, duración, pasajeros).\n+* Capado de cardinalidad de `pu_location_id` (IDs > 265 agrupados).\n+* Split temporal fijo: Train (<=2022), Validación (2023), Test (2024).\n+* Transformaciones: `StandardScaler` para numéricas y `OneHotEncoder(handle_unknown='ignore', max_categories=50)` para categóricas dentro de un `ColumnTransformer`.\n+* Se eliminaron polígonos/polimorfismo y generación polinomial para priorizar interpretabilidad y velocidad en ensembles.\n+\n+Muestreo y Estrategia de Carga:\n+* Extracción vía Spark JDBC desde `analytics.obt_trips` con query parametrizada y `random() <= 0.02` para generar una muestra balanceada multianual.\n+* Particionamiento por año para lectura paralela y deduplicación antes de pasar a Pandas.\n+\n+Entrenamiento y Búsqueda de Hiperparámetros:\n+* `TimeSeriesSplit(n_splits=5)` para respetar el orden temporal en Gradient Boosting y LightGBM.\n+* Grids concisos enfocándose en profundidad, tasa de aprendizaje, número de estimadores y subsampling (`subsample`, `colsample_bytree`).\n+* Registro de tiempos de ajuste (segundos) para comparar costo computacional vs. mejora predictiva.\n+\n+Evaluación:\n+* Métricas: RMSE y MAE principales; R² como referencia de varianza explicada.\n+* Selección del modelo final por menor RMSE en validación (2023).\n+* Evaluación final en Test (2024) sólo con el mejor pipeline para evitar sobre-reporting.\n+\n+Hallazgos Clave:\n+* LightGBM y Gradient Boosting ofrecen mejor trade-off entre error y estabilidad temporal.\n+* Bagging vs Pasting evidencian el impacto positivo del bootstrap bajo alta variabilidad de ubicaciones.\n+* VotingRegressor estabiliza pero no siempre supera a boosting cuando las relaciones no lineales dominan.\n+\n+Próximos pasos potenciales (no implementados aún):\n+* Stacking de nivel 2 (meta-modelo).\n+* Ajuste de tasa de muestreo dinámica por año para balances finos.\n+* Incorporar características derivadas de distancia temporal (festivos, clima).\n+\n+Checklist actualizado añade:\n+[x] Modelos Ensemble (Voting, Bagging, Gradient Boosting, LightGBM) comparados con baseline.\n+\n+Dependencias adicionales requeridas para esta fase (agregar en `requirements.txt` si se desea reproducibilidad directa): `scikit-learn`, `lightgbm`, `seaborn`, `matplotlib`, `python-dotenv`, `snowflake-connector-python`, `pyspark`.\n+\n+El modelo ganador se determina con base en el menor RMSE de validación manteniendo consistencia del MAE y sin degradar significativamente R².\n+```
