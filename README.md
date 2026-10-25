# 🏠 WorthIT — AI-Powered Real Estate Price Predictor

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
*   **City-Specific Growth Rates:** Dynamically adjusts for cities like Mumbai (9%), Bangalore (8%), Chennai (6%), Kolkata (5%).
*   **Investment Scoring:** Categorises investments as *Good*, *Moderate*, or *Risky* based on predicted yield.

### 🗺️ Visual Price Heatmap
*   **Google Maps Integration:** Explore property pricing trends across different locations via an interactive heatmap powered by the **Google Maps JavaScript API**.
*   Displays up to 250 averaged location data points for fast rendering.

### 🔒 User Management
*   Secure authentication system (username/password + **Google OAuth2**) for saving searches and accessing personalised dashboards.
*   Prediction history is stored per user account.

### 🌐 Professional Website Footer
*   Privacy Policy, Terms of Service, Cookie Policy, and Disclaimer (modal-based).
*   Help & FAQ accordion panel.
*   Contact: [nandishkumar01122005@gmail.com](mailto:nandishkumar01122005@gmail.com)
*   Report bugs on [GitHub Issues](https://github.com/NandishKumar2005/Smart_Real_Estate_Price_Predictor/issues).

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3, Django, Django REST Framework |
| **Machine Learning** | Scikit-learn (Random Forest), Pandas, NumPy, Joblib |
| **Frontend** | HTML5, CSS3 (Glassmorphism / Dark Mode), Bootstrap 5, JavaScript (ES6+) |
| **Mapping** | **Google Maps JavaScript API** (HeatmapLayer + geocoded markers) |
| **Auth** | Django sessions + **Google OAuth 2.0** |
| **Database** | SQLite (default), scalable to PostgreSQL |
| **Deployment** | Vercel (serverless) via `vercel.json` |

---

## ⚙️ Installation & Setup

Follow these steps to set up the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/NandishKumar2005/Smart_Real_Estate_Price_Predictor.git
cd Smart_Real_Estate_Price_Predictor
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

### 4. Environment Variables
Create a `.env` file (or set in your shell) with:
```
DJANGO_SECRET_KEY=your-secret-key
GOOGLE_OAUTH_CLIENT_ID=your-google-oauth-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-oauth-client-secret
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Model Training (Optional / First Time)
To refresh the model with current data:
```bash
python ml/train_model.py
```
*Note: This generates `house_price_model.pkl` and `locations.pkl` in the `ml/` directory.*

### 7. Run the Application
```bash
python manage.py runserver
```

---

## 🧪 Testing

A comprehensive test suite is included for the **ST & QA** module, covering all major layers of the application.

### Run All Tests
```bash
venv\Scripts\python.exe -m pytest tests\ -v
```

| Test File | Category | Cases |
|---|---|---|
| `tests/test_whitebox.py` | White Box Testing | WB01–WB06 (22 tests) |
| `tests/test_ml.py` | ML Model Testing | ML01–ML04 (18 tests) |
| `tests/test_api.py` | API Testing | API01–API03 (15 tests) |
| `tests/test_integration.py` | Integration Testing | IT01–IT03 (12 tests) |
| **Total** | | **67 tests** |

> **Bug found & fixed during WB06:** A `ZeroDivisionError` was discovered when `price=0` was passed to `InvestmentAdvisor`. A guard clause was added to `services/investment_advisor.py` to return safe defaults.

---

## 📂 Project Structure

```text
Smart_Real_Estate_Price_Predictor/
├── ml/                     # ML training scripts and serialised models (.pkl)
│   ├── train_model.py      # Random Forest training pipeline
│   ├── preprocess.py       # Feature engineering / preprocessing
│   ├── house_price_model.pkl
│   └── locations.pkl
├── predictor/              # Main Django app (views, URLs, models, serialisers)
├── real_estate_ai/         # Project settings and root URL configuration
├── services/               # Core business logic
│   ├── prediction_service.py   # Singleton ML prediction wrapper
│   └── investment_advisor.py   # ROI & investment score calculator
├── static/                 # CSS, JS, Images
├── templates/              # HTML templates (base, home, predict, heatmap, dashboard)
├── tests/                  # Full ST&QA test suite (67 tests)
├── requirements.txt
├── manage.py
└── vercel.json             # Serverless deployment config
```

---

## 🗺️ Google Maps API Setup

The heatmap feature uses the **Google Maps JavaScript API** with the `visualization` library:

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **Maps JavaScript API**.
3. Create an API key and restrict it to your domain.
4. Set `GOOGLE_MAPS_API_KEY` in your environment variables.

The key is injected server-side via Django's template context — it is **never exposed in source code**.

---

## 🏆 Project Highlights

- **Premium UI:** Glassmorphism effects, smooth animations, and a dynamic dark/light theme toggle.
- **Professional Footer:** Privacy Policy, Terms of Service, Cookie Policy, Disclaimer, and Help/FAQ — all available as accessible modals on every page.
- **Data-Driven:** Pre-processing pipeline handles outlier removal and feature engineering for better model accuracy.
- **RESTful API:** `/api/predict-price` and `/api/price-heatmap` endpoints power both the UI and support external integrations.
- **Google OAuth2:** One-click sign-in via Google account.
- **67-Test Suite:** White Box, ML Model, API, and Integration tests demonstrating professional QA practices.

---

## 📝 License

This project is developed for educational purposes as part of an academic curriculum. Feel free to use and adapt with attribution.

**Contact:** [nandishkumar01122005@gmail.com](mailto:nandishkumar01122005@gmail.com)
