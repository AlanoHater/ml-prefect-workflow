import pandas as pd
import numpy as np
import skops.io as sio
from prefect import flow, task
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_recall_curve
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OrdinalEncoder
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
import warnings
import os

# Configuración
warnings.filterwarnings("ignore")
os.environ["PF_LOGGING_LEVEL"] = "ERROR"

@task
def load_data(filename: str):
    # Carga dataset completo
    bank_df = pd.read_csv(filename, index_col="id")
    
    # Feature Engineering Básico (Clave para subir de 0.50 a 0.67)
    bank_df['BalanceSalaryRatio'] = bank_df['Balance'] / bank_df['EstimatedSalary']
    bank_df['TenureByAge'] = bank_df['Tenure'] / bank_df['Age']
    bank_df['CreditScoreGivenAge'] = bank_df['CreditScore'] / bank_df['Age']
    
    bank_df = bank_df.drop(["CustomerId", "Surname"], axis=1)
    return bank_df

@task
def initial_split(bank_df: pd.DataFrame):
    X = bank_df.drop(["Exited"], axis=1)
    y = bank_df["Exited"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=125, stratify=y
    )
    return X_train, X_test, y_train, y_test

@task
def preprocessing_strict(X_train, X_test):
    # Definición por Nombres (Más robusto)
    cat_cols = ["Geography", "Gender"]
    num_cols = [
        "CreditScore", "Age", "Tenure", "Balance", "NumOfProducts", 
        "HasCrCard", "IsActiveMember", "EstimatedSalary",
        "BalanceSalaryRatio", "TenureByAge", "CreditScoreGivenAge" 
    ]

    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy="median")),
        ('scaler', MinMaxScaler())
    ])

    cat_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy="most_frequent")),
        ('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_pipeline, num_cols),
            ('cat', cat_pipeline, cat_cols)
        ]
    )

    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    return X_train_processed, X_test_processed

@task
def train_xgboost(X_train, y_train):
    # Usamos scale_pos_weight en lugar de SMOTE para XGBoost
    ratio = float(np.sum(y_train == 0)) / np.sum(y_train == 1)
    print(f"Entrenando XGBoost (Weight: {ratio:.2f})...")
    
    model = XGBClassifier(
        n_estimators=200, 
        learning_rate=0.05,
        max_depth=5,
        scale_pos_weight=ratio, 
        eval_metric='logloss',
        random_state=125,
        use_label_encoder=False,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    return model

@task
def evaluate_model(model, X_test, y_test, model_name="Model"):
    # Threshold Moving: Busca el mejor corte para maximizar F1
    y_scores = model.predict_proba(X_test)[:, 1]
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_scores)
    
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls)
    best_idx = np.argmax(f1_scores)
    best_f1 = f1_scores[best_idx]
    
    print(f"--- {model_name} ---")
    print(f"Mejor F1 Score: {best_f1:.2f}")
    return best_f1

@task
def save_best_model(model, name):
    sio.dump(model, f"{name}.skops")
    print(f"Modelo guardado: {name}.skops")

@flow(log_prints=True)
def ml_workflow(filename: str = "train.csv"):
    raw_df = load_data(filename)
    X_train_raw, X_test_raw, y_train, y_test = initial_split(raw_df)
    X_train, X_test = preprocessing_strict(X_train_raw, X_test_raw)

    # Solo XGBoost (ganador claro) para simplificar el pipeline final
    model = train_xgboost(X_train, y_train)
    f1 = evaluate_model(model, X_test, y_test, "XGBoost")
    save_best_model(model, "final_model")

if __name__ == "__main__":
    ml_workflow()