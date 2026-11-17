import pandas as pd

data = {
    "Metric": [
        "Accuracy",
        "Balanced Accuracy",
        "ROC-AUC",
        "Flood Precision",
        "Flood Recall",
        "Flood F1-Score"
    ],
    "Random Forest": [
        0.8716,
        0.6943,
        0.8293,
        0.46,
        0.46,
        0.46
    ],
    "XGBoost": [
        0.8716,
        0.5946,
        0.8069,
        0.43,
        0.23,
        0.30
    ]
}

df = pd.DataFrame(data)

df.to_csv(
    "datasets/processed/model_comparison.csv",
    index=False
)

print(df)
print("\nModel comparison saved successfully.")