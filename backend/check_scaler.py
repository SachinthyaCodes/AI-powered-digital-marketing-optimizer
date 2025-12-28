"""
Script to extract y_scaler from the trained model or recreate it
Run this if y_scaler.pkl is missing
"""

import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os

# Check if y_scaler.pkl exists
SCALER_PATH = os.path.join("SavedModels", "y_scaler.pkl")

if os.path.exists(SCALER_PATH):
    print(f"✅ y_scaler.pkl already exists at {SCALER_PATH}")
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
    print(f"Scaler mean: {scaler.mean_}")
    print(f"Scaler scale: {scaler.scale_}")
else:
    print(f"⚠️  y_scaler.pkl not found at {SCALER_PATH}")
    print("Please run the reach.ipynb notebook to train the model and save the scaler")
    print("\nAlternatively, if you have the training data, this script can recreate it:")
    
    # Try to recreate from datasets
    try:
        base_dir = "Datasets"
        paths = [os.path.join(base_dir, f"Dataset{i}.xlsx") for i in range(1, 6)]
        
        dfs = []
        for p in paths:
            if os.path.exists(p):
                df = pd.read_excel(p)
                if "Estimated_Clicks" in df.columns:
                    df = df.rename(columns={"Estimated_Clicks": "clicks"})
                dfs.append(df)
        
        if dfs:
            full = pd.concat(dfs, ignore_index=True)
            targets = ["likes", "comments", "shares", "clicks", "timing_quality_score"]
            full = full.dropna(subset=targets)
            
            # Log transform
            for col in ["likes", "comments", "shares", "clicks"]:
                full[col] = np.log1p(full[col])
            
            y_raw = full[targets].values.astype("float32")
            y_scaler = StandardScaler()
            y_scaler.fit(y_raw)
            
            # Save
            os.makedirs("SavedModels", exist_ok=True)
            with open(SCALER_PATH, "wb") as f:
                pickle.dump(y_scaler, f)
            
            print(f"✅ y_scaler.pkl recreated and saved at {SCALER_PATH}")
            print(f"Scaler mean: {y_scaler.mean_}")
            print(f"Scaler scale: {y_scaler.scale_}")
        else:
            print("❌ No dataset files found. Please run reach.ipynb to train the model.")
    
    except Exception as e:
        print(f"❌ Error recreating scaler: {e}")
        print("Please run reach.ipynb to train the model and save all artifacts.")
