import os
import sys

# Add the project root to the Python path so we can import ml.preprocess
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
from ml.preprocess import build_preprocessor
from sklearn.pipeline import Pipeline

def load_and_prep_data():
    dataset_path = os.path.join(os.path.dirname(__file__), 'merged_files.csv')
    print(f"Loading dataset from {dataset_path}...")
    
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}. Please place 'merged_files.csv' in the ml directory.")
        
    df = pd.read_csv(dataset_path)
    
    # 1. Select and rename required columns
    # We need: Price, Area, Location, City, No. of Bedrooms, Resale
    cols_to_keep = ['Price', 'Area', 'Location', 'City', 'No. of Bedrooms', 'Resale']
    df = df[[c for c in cols_to_keep if c in df.columns]].copy()
    
    df.rename(columns={
        'Price': 'price',
        'Area': 'area',
        'No. of Bedrooms': 'bhk'
    }, inplace=True)
    
    # Drop rows with NaNs in critical columns
    df.dropna(subset=['price', 'area', 'Location', 'City', 'bhk'], inplace=True)
    
    # 2. Clean Location
    # Combine Location and City into a single precise string exactly how the dropdown will show it
    df['location'] = df['Location'].str.strip() + ", " + df['City'].str.strip()
    
    # 3. Synthesize missing form fields (Bathrooms, Age) using clever proxies
    np.random.seed(42)  # for reproducibility
    
    # Bathrooms: Usually equal to BHK or BHK-1
    df['bathrooms'] = np.where(np.random.rand(len(df)) > 0.2, df['bhk'], np.maximum(1, df['bhk'] - 1))
    
    # Age: Based on 'Resale' flag if present. Resale=1 means older, Resale=0 means new.
    if 'Resale' in df.columns:
        df['age'] = np.where(df['Resale'] == 1, 
                             np.random.randint(4, 25, size=len(df)), 
                             np.random.randint(0, 3, size=len(df)))
    else:
        df['age'] = np.random.randint(1, 15, size=len(df))
        
    # 4. Outlier Removal (Optional but recommended for Random Forests)
    # Remove extremely crazy prices or areas to prevent the model from skewing
    # E.g. Area < 100 or Area > 10000, Price < 100000 (1 Lakh) or Price > 500000000 (50 Crores)
    df = df[(df['area'] >= 200) & (df['area'] <= 15000)]
    df = df[(df['price'] >= 500000) & (df['price'] <= 250000000)]
    
    # Map to final expected Schema
    final_df = df[['location', 'area', 'bhk', 'bathrooms', 'age', 'price']].copy()
    
    print(f"Data prepped! Total samples: {len(final_df)}")
    return final_df

def train_and_save():
    df = load_and_prep_data()
    
    X = df.drop('price', axis=1)
    y = df['price']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    preprocessor = build_preprocessor()
    
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, max_depth=20, n_jobs=-1, random_state=42))
    ])
    
    print("Training model (this might take a few seconds with real data)...")
    model.fit(X_train, y_train)
    
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"R2 Score: {r2:.4f}")
    print(f"RMSE: {rmse:,.2f} INR")
    
    model_path = os.path.join(os.path.dirname(__file__), 'house_price_model.pkl')
    print(f"Saving model to {model_path}...")
    joblib.dump(model, model_path)
    
    # Optional: Save a list of unique locations so the frontend can populate them
    locations_path = os.path.join(os.path.dirname(__file__), 'locations.pkl')
    unique_locations = sorted(df['location'].unique().tolist())
    joblib.dump(unique_locations, locations_path)
    print(f"Saved {len(unique_locations)} unique locations to {locations_path}")
    
    print("Done!")

if __name__ == "__main__":
    train_and_save()
