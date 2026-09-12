import pandas as pd
from pathlib import Path

BASE_PATH = Path("data")

print("Loading geopolitical zones...")
df_geo = pd.read_csv(BASE_PATH / "raw" / "1_gp_zones.csv")
print(f"✓ Loaded {len(df_geo)} rows")
print(df_geo.head())

print("\nLoading pidgin data...")
df_pidgin = pd.read_csv(BASE_PATH / "raw" / "2_pidgin_state.csv")
print(f"✓ Loaded {len(df_pidgin)} rows")
print(df_pidgin.head())

print("\nLoading EFInA data...")
df_efinadata = pd.read_csv(BASE_PATH / "raw" / "3_efindata_2023.csv")
print(f"✓ Loaded {len(df_efinadata)} rows")
print(df_efinadata.head())

print("\n" + "="*80)
print("ALL DATA LOADED SUCCESSFULLY. NO API NEEDED.")
print("="*80)