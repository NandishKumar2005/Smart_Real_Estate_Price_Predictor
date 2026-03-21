# 🏠 Real Estate Predictor (AI-Powered)

An advanced, machine learning-driven real estate platform for predicting property prices and analyzing investment opportunities in major Indian cities. This project integrates a Django-based web application with modern AI models to provide accurate, data-backed insights for homebuyers and investors.

---

## ✨ Key Features

### 🚀 Smart Price Prediction
Predict real estate prices based on multiple property parameters:
*   **Precise Locations:** Covers 1,400+ specific locations across major Indian metropolises.
*   **Key Amenities:** Factors in area (sq. ft.), number of BHKs, bathrooms, and property age.
*   **Machine Learning Engine:** Powered by a **Random Forest Regressor** trained on real estate market data.

### 📊 Investment Advisor
Integrated AI-powered investment analysis that provides:
*   **ROI Projection:** 5-year expected appreciation forecasts.
*   **City-Specific Growth Rates:** Dynamically adjusts for cities like Mumbai, Bangalore, Chennai, etc.
*   **Investment Scoring:** Categorizes investments as 'Good', 'Moderate', or 'Risky' based on predicted yield.

### 🗺️ Visual Analytics
*   **Heatmap Visualization:** Explore property density and pricing trends across different locations via an interactive map (powered by Leaflet.js).
*   **History Dashboard:** Track and manage your previous price predictions.

### 🔒 User Management
*   Secure authentication system for saving searches and accessing personalized dashboards.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python, Django |
| **Machine Learning** | Scikit-learn (Random Forest), Pandas, NumPy, Joblib |
| **Frontend** | HTML5, CSS3 (Modern Aesthetic), JavaScript (ES6+), Leaflet.js |
| **Database** | SQLite (Default), scalable to PostgreSQL/MySQL |

---

## ⚙️ Installation & Setup

Follow these steps to set up the project locally:

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Real_Estate_Predictor
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Model Training (Optional/First Time)
To refresh the model with current data:
```bash
python ml/train_model.py
```
*Note: This generates `house_price_model.pkl` and `locations.pkl` in the `ml/` directory.*

### 6. Run the Application
```bash
python manage.py runserver
```

---

## 📂 Project Structure

```text
Real_Estate_Predictor/
├── ml/                # ML training scripts and serialized models (.pkl)
├── predictor/         # Main Django app handling logic, views, and APIs
├── real_estate_ai/    # Project configuration and URL routing
├── services/          # Core modules for prediction and investment logic
├── static/            # Frontend assets (CSS, JS, Images)
├── templates/         # HTML templates (Heatmap, Prediction, Dashboard)
└── manage.py          # Django management entry point
```

---

## 🏆 Project Highlights
- **Premium UI:** Features glassmorphism effects, smooth animations, and a dynamic dark/light theme.
- **Data-Driven:** Preprocessing pipeline handles outlier removal and feature engineering for better accuracy.
- **RESTful Ready:** Includes API endpoints for predictions and data visualizations.

---

## 📝 License
This project is for users who really need to invest in real estate business. Feel free to use and adapt!
