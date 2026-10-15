import io
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

def get_excel_sheet_names(uploaded_file) -> Optional[List[str]]:
    """Return sheet names if the uploaded file is an Excel file, else None."""
    name = uploaded_file.name.lower()
    if name.endswith(('.xlsx', '.xls')):
        uploaded_file.seek(0)
        excel_file = pd.ExcelFile(uploaded_file)
        return excel_file.sheet_names
    return None

def load_data(uploaded_file, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Load data from uploaded file (xlsx, xls, csv) or file path."""
    if isinstance(uploaded_file, str):
        # Local file path
        if uploaded_file.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        else:
            return pd.read_excel(uploaded_file, sheet_name=sheet_name or 0)

    # Streamlit UploadedFile object
    name = uploaded_file.name.lower()
    uploaded_file.seek(0)
    if name.endswith('.csv'):
        # Try utf-8, fallback to big5 or latin1
        try:
            return pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            try:
                return pd.read_csv(uploaded_file, encoding='big5')
            except Exception:
                uploaded_file.seek(0)
                return pd.read_csv(uploaded_file, encoding='latin1')
    elif name.endswith(('.xlsx', '.xls')):
        return pd.read_excel(uploaded_file, sheet_name=sheet_name or 0)
    else:
        raise ValueError("不支援的檔案格式，請上傳 .xlsx, .xls 或 .csv 檔案。")

def classify_columns(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Classify DataFrame columns into numeric, categorical, datetime, and text."""
    numeric_cols = []
    categorical_cols = []
    datetime_cols = []
    text_cols = []

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # If numeric with very few unique values (e.g. 0/1 or 1/2/3), it can be used as categorical too
            numeric_cols.append(col)
            if df[col].nunique() <= 5:
                categorical_cols.append(col)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
        else:
            # Check unique values
            unique_ratio = df[col].nunique() / max(len(df[col]), 1)
            if df[col].nunique() <= 30 or unique_ratio < 0.2:
                categorical_cols.append(col)
            else:
                text_cols.append(col)

    return {
        'numeric': numeric_cols,
        'categorical': categorical_cols,
        'datetime': datetime_cols,
        'text': text_cols,
        'all': list(df.columns)
    }

def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return summary of missing values in the dataframe."""
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df)) * 100
    summary = pd.DataFrame({
        '欄位名稱': df.columns,
        '資料型態': [str(df[col].dtype) for col in df.columns],
        '非空值筆數': df.notnull().sum(),
        '缺失值筆數': missing_count,
        '缺失比例 (%)': missing_pct.round(2)
    }).reset_index(drop=True)
    return summary

def get_sample_datasets() -> Dict[str, str]:
    """Return dictionary of available built-in sample datasets."""
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_data')
    samples = {}
    if os.path.exists(sample_dir):
        for f in os.listdir(sample_dir):
            if f.endswith(('.xlsx', '.csv')):
                label = f.replace('_', ' ').replace('.xlsx', '').replace('.csv', '').title()
                samples[label] = os.path.join(sample_dir, f)
    return samples
