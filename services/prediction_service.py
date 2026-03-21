import os
import joblib # pyright: ignore[reportMissingImports]
import pandas as pd # type: ignore
# from django.conf import settings

class PredictionService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PredictionService, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        try:
            # We must add project root to path in case the ml module needs it, but it should be fine since it's in the same project root
            # Replace settings.BASE_DIR with a direct path or environment variable
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, 'ml', 'house_price_model.pkl')
            self._model = joblib.load(model_path)
        except Exception as e:
            print(f"Error loading model: {e}")
            self._model = None

    def predict(self, location, area, bhk, bathrooms, age):
        """
        Takes input features, preprocesses them, and returns the predicted price.
        """
        if self._model is None:
            raise ValueError("Model is not loaded. Cannot make predictions.")
        
        # Create a dataframe from input for the pipeline
        input_data = pd.DataFrame([{
            'location': location,
            'area': area,
            'bhk': bhk,
            'bathrooms': bathrooms,
            'age': age
        }])
        
        # The pipeline handles preprocessing automatically
        predicted_price = self._model.predict(input_data)[0]
        
        return int(max(0, predicted_price))  # Ensure non-negative and return as int
