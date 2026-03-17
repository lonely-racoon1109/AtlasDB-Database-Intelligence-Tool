import pandas as pd

def generate_schema(tables):

    schema = {}

    column_usage = {}
    pk_map = {}
    fk_map = {}

    # Track where columns appear
    for table_name, df in tables.items():
        for col in df.columns:
            column_usage.setdefault(col, []).append(table_name)

    # DETECT PK CANDIDATES
    pk_candidates = {}

    for table_name, df in tables.items():

        rows = len(df)

        for col in df.columns:

            if not col.lower().endswith("_id"):
                continue

            missing = df[col].isna().sum()
            unique = df[col].nunique()

            if missing != 0:
                continue

            ratio = unique / rows

            # strong PK signal
            if ratio >= 0.98:

                if col not in pk_candidates or ratio > pk_candidates[col]["ratio"]:
                    pk_candidates[col] = {
                        "table": table_name,
                        "ratio": ratio
                    }


    # ASSIGN PK
    for col, data in pk_candidates.items():
        pk_map[col] = data["table"]


    # DETECT FK
    for col, tables_list in column_usage.items():

        if col not in pk_map:
            continue

        pk_table = pk_map[col]

        for table in tables_list:

            if table != pk_table:
                fk_map.setdefault(table, []).append(col)


    # Build Schema 
    for table_name, df in tables.items():

        columns = {}

        for col in df.columns:

            missing = int(df[col].isna().sum())
            unique = int(df[col].nunique())

            constraint = []

            if col in pk_map and pk_map[col] == table_name:
                constraint.append("PK")

            elif table_name in fk_map and col in fk_map[table_name]:
                constraint.append("FK")

            columns[col] = {
                "dtype": str(df[col].dtype),
                "missing": missing,
                "unique": unique,
                "constraints": ", ".join(constraint),
            }

        schema[table_name] = {
            "rows": len(df),
            "columns": columns
        }

    return schema