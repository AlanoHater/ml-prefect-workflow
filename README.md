# Bank Customer Churn Prediction Pipeline (Orchestrated with Prefect)


## 1. Model Summary and Performance

| Feature | Detail | Source |
| :--- | :--- | :--- |
| **Problem Type** | Binary Classification (Predicting customer exit: 0 or 1) | Kaggle |
| **Model** | XGBoost Classifier | Sklearn |
| **Optimization** | Class Imbalance handled via `scale_pos_weight` | |
| **Main Metric** | F1 Score (Optimized via Threshold Moving) | |
| **Current F1** | ~0.67 | |

## 2. Pipeline Architecture and Flow

The entire workflow is structured using Prefect's `@flow` and `@task` decorators, ensuring each stage is atomic and traceable.

### Task Breakdown

1.  **`load_data`**: Loads the full `train.csv` dataset. This is the only task where **Feature Engineering** is applied, creating new interaction variables before data splitting.
    * **Features Added:** `BalanceSalaryRatio`, `TenureByAge`, `CreditScoreGivenAge`.
2.  **`initial_split`**: Splits the data into 70% train and 30% test, ensuring the class distribution (`stratify=y`) remains balanced across both sets.
3.  **`preprocessing_strict`**: Utilizes a `ColumnTransformer` to apply standard scaling (`MinMaxScaler`) to numerical features and encoding (`OrdinalEncoder`) to categorical features. The process fits transformers **only** on the training data to prevent data leakage.
4.  **`train_xgboost`**: Trains the model using the calculated imbalance ratio (`scale_pos_weight`) to natively handle the minority class without relying on synthetic data generation (SMOTE).
5.  **`evaluate_model`**: Instead of using the default 0.5 threshold, this task calculates the optimal cutoff point to maximize the F1 Score on the test set.
6.  **`save_best_model`**: Serializes the final trained model using the `skops` library.

## 3. Orchestration and Deployment (MLOps)

The **Deployment** serves as the managed execution unit for the workflow.

* **Automation:** The deployment enables scheduled runs (e.g., weekly re-training via CRON) to keep the model current with evolving customer data.
* **Work Pool:** The deployment targets a **Work Pool** (managed by a Prefect Worker/Agent) which allocates the necessary compute resources to execute the Python code.
* **Resilience:** The orchestration layer provides built-in features like automated logging, monitoring, and configurable retries in case of task failures (e.g., temporary network errors during data loading or training spikes).

The ultimate goal of the deployment is to operationalize the XGBoost model by ensuring its reliability and continuous, automated execution in a production-like environment.
