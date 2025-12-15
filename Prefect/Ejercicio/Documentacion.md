# Bank Customer Churn Prediction Pipeline

Este proyecto implementa un pipeline de Machine Learning orquestado con **Prefect** para predecir la fuga de clientes bancarios (Churn). Utiliza **XGBoost** como modelo principal, optimizado para datos desbalanceados.

## 1. Resumen del Modelo

* **Tipo de Problema:** Clasificación Binaria (0 = No Churn, 1 = Churn).
* **Modelo:** XGBoost Classifier (`scale_pos_weight` ajustado).
* **Métrica Principal:** F1 Score (Optimizado mediante ajuste de umbral).
* **Performance Actual:** ~0.67 F1 Score / ~86% Accuracy.
* **Input:** Datos tabulares de clientes (Score crediticio, geografía, edad, balance, etc.).
* **Output:** Probabilidad de fuga y clasificación binaria.

## 2. Arquitectura del Pipeline (Prefect)

El flujo está dividido en tareas atómicas gestionadas por Prefect para asegurar observabilidad y manejo de fallos:

1.  **Load Data:** Carga el dataset completo y aplica *Feature Engineering* inicial.
2.  **Initial Split:** Divide en Train/Test (70/30) usando estratificación para mantener la proporción de clases.
3.  **Preprocessing:**
    * Imputación de valores nulos (Mediana para numéricos, Moda para categóricos).
    * Escalado MinMax para variables numéricas.
    * Ordinal Encoding para variables categóricas.
4.  **Training:** Entrena XGBoost penalizando errores en la clase minoritaria.
5.  **Evaluation:** Calcula métricas y encuentra el umbral de decisión óptimo (Threshold Moving).
6.  **Serialization:** Guarda el modelo entrenado en formato `.skops`.

## 3. Ingeniería de Características (Feature Engineering)

Se generan tres variables sintéticas para aumentar la capacidad predictiva del modelo:

* `BalanceSalaryRatio`: Relación entre el saldo bancario y el salario estimado. Ayuda a identificar clientes con alta liquidez vs. ingresos.
* `TenureByAge`: Antigüedad normalizada por la edad.
* `CreditScoreGivenAge`: Comportamiento crediticio relativo a la etapa de vida del cliente.

## 4. Explicación del Código (`main.py`)

### Configuración
Se configuran los logs de Prefect y se suprimen advertencias innecesarias de Pandas/Sklearn para mantener la consola limpia.

### Tareas (`@task`)

* **`load_data`**:
    * Carga el CSV `train.csv`.
    * **Crucial:** Genera las nuevas columnas matemáticas antes de cualquier división.
    * Elimina columnas irrelevantes (`CustomerId`, `Surname`).

* **`initial_split`**:
    * Separa `X` (features) e `y` (target).
    * Usa `stratify=y` para garantizar que Train y Test tengan el mismo porcentaje de casos de abandono.

* **`preprocessing_strict`**:
    * Define explícitamente qué columnas son numéricas y cuáles categóricas por **nombre**.
    * Usa `ColumnTransformer` para aplicar transformaciones diferenciadas.
    * **Regla de Oro:** Hace `fit` solo en Train y `transform` en Test para evitar *Data Leakage*.

* **`train_xgboost`**:
    * Calcula el ratio de desbalance (Negativos / Positivos).
    * Usa `scale_pos_weight=ratio` para que el modelo preste más atención a la clase minoritaria (Churn) sin necesidad de crear datos falsos (SMOTE).
    * Hiperparámetros conservadores (`learning_rate=0.05`, `max_depth=5`) para evitar sobreajuste.

* **`evaluate_model`**:
    * No usa el corte estándar de 0.5.
    * Genera una curva de Precisión-Recall.
    * Calcula dinámicamente qué probabilidad de corte maximiza el F1 Score.

* **`ml_workflow` (`@flow`)**:
    * Función principal que orquesta el orden de ejecución.
    * Pasa los datos de una tarea a otra.
    * Decide qué modelo guardar al final.

## 5. Requisitos
* Python 3.9+
* Prefect 3.x
* Scikit-learn / Skops
* XGBoost
* Pandas / Numpy