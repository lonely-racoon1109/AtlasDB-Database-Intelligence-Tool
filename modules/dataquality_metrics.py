import pandas as pd

def generate_data_quality(tables):
    dq_summary = {}
    for table_name, df in tables.items():
        numeric_df = df.select_dtypes(include="number")
        if numeric_df.shape[1] > 0:
            numeric_stats = numeric_df.describe().to_dict()
        else:
            numeric_stats = {}
        dq_summary[table_name] = {
            "rows": len(df),
            "columns": df.shape[1],
            "completeness": round(df.notnull().mean().mean() * 100, 2), 
            "duplicates": df.duplicated().sum(),
            "duplicate_rate":round((df.duplicated().sum() / len(df)) * 100, 2) if len(df) else 0,
            "null_heavy_cols": [col for col in df.columns if df[col].isnull().mean() > 0.5],
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1e6, 2),
            "numeric_cols": df.select_dtypes(include="number").columns.tolist(),
            "categorical_cols": df.select_dtypes(include="object").columns.tolist()
        }
    return dq_summary