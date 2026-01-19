
import pandas as pd

try:
    df = pd.read_excel("RelatorioDeEventos - 19_01_2026 - 19_01_2026.xls", engine="xlrd")
    print("Columns:", df.columns.tolist())
    print("First 5 rows:\n", df.head())
    print("Dtypes:\n", df.dtypes)
except Exception as e:
    print(f"Error: {e}")
