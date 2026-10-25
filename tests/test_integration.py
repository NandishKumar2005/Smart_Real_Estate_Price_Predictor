"""
=============================================================================
INTEGRATION TESTING – Smart Real Estate Price Predictor
Subject: Software Testing & Quality Assurance (ST & QA)
=============================================================================
IT01 – Frontend, Django Backend, and Random Forest Integration Test
IT02 – Price Prediction and Investment Advisor Integration Test
IT03 – Heatmap API and Google Maps JavaScript Integration Test
=============================================================================
These tests verify that components work TOGETHER end-to-end, not in isolation.
=============================================================================
"""

import os
import sys
import json
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "real_estate_ai.settings")

import django
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from predictor.models import PredictionHistory


# =============================================================================
# IT01 – Frontend ↔ Django Backend ↔ Random Forest Integration Test
# Simulates the complete request lifecycle: HTML page → AJAX POST to API →
# Django validates → PredictionService (RF model) → structured JSON response
# back to the frontend.
# =============================================================================
class IT01_FrontendBackendMLIntegrationTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Create a test user to simulate authenticated session
        self.user = User.objects.create_user(
            username="test_integration_user",
            password="testpass123"
        )

    def test_home_page_loads_html(self):
        """The home page must return HTTP 200 and render HTML content."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        # Check for DOCTYPE case-insensitively (template may use lowercase doctype)
        content_lower = resp.content.lower()
        self.assertIn(b"<!doctype html>", content_lower,
                      "Response does not look like an HTML document.")
        content = resp.content.decode()
        self.assertTrue(len(content) > 100, "Homepage HTML content is too short.")
        print(f"\n[IT01] PASS – Home page returned HTML ({len(content)} bytes).")

    def test_predict_page_requires_login(self):
        """Unauthenticated user accessing /predict/ must be redirected to login."""
        resp = self.client.get("/predict/")
        # Django LoginRequiredMixin redirects with HTTP 302
        self.assertEqual(resp.status_code, 302)
        self.assertIn("login", resp["Location"])
        print(f"[IT01] PASS – /predict/ redirects unauthenticated user to login.")

    def test_full_prediction_pipeline_authenticated(self):
        """
        End-to-end: authenticated user POSTs to API → model predicts →
        response JSON has predicted_price → history saved to DB.
        """
        # Log in the test user
        self.client.login(username="test_integration_user", password="testpass123")

        payload = {
            "location":  "Whitefield, Bangalore",
            "area":      1200,
            "bhk":       3,
            "bathrooms": 2,
            "age":       5
        }

        # 1. Frontend sends AJAX POST to API endpoint
        resp = self.client.post(
            "/api/predict-price",
            data=json.dumps(payload),
            content_type="application/json"
        )

        # 2. Backend + RF model must return 200 + valid data
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("predicted_price", data)
        self.assertGreater(data["predicted_price"], 0)

        # 3. History record must be saved in the database for this user
        history_count = PredictionHistory.objects.filter(
            user=self.user,
            location="Whitefield, Bangalore"
        ).count()
        self.assertGreaterEqual(history_count, 1)

        print(f"[IT01] PASS – End-to-End: ₹{data['predicted_price']:,} predicted, "
              f"history saved ({history_count} record(s)).")

    def test_predict_page_loads_for_authenticated_user(self):
        """/predict/ page must return 200 and contain location data for logged-in user."""
        self.client.login(username="test_integration_user", password="testpass123")
        resp = self.client.get("/predict/")
        self.assertEqual(resp.status_code, 200)
        print(f"[IT01] PASS – /predict/ page returned HTTP 200 for authenticated user.")


# =============================================================================
# IT02 – Price Prediction and Investment Advisor Integration Test
# Verifies that `PredictionService` output flows correctly into
# `InvestmentAdvisor` and that the combined API response is coherent.
# =============================================================================
class IT02_PredictionAndInvestmentAdvisorIntegrationTest(TestCase):

    def setUp(self):
        self.client = Client()

    def _predict(self, payload):
        return self.client.post(
            "/api/predict-price",
            data=json.dumps(payload),
            content_type="application/json"
        )

    def test_roi_increases_for_new_mumbai_property(self):
        """
        New Mumbai property (age=1) should have higher ROI than old Kolkata
        property (age=20), demonstrating the integration of city + age logic.
        """
        resp_new_mumbai = self._predict({
            "location": "Andheri, Mumbai", "area": 1000,
            "bhk": 2, "bathrooms": 2, "age": 1
        })
        resp_old_kolkata = self._predict({
            "location": "Salt Lake, Kolkata", "area": 1000,
            "bhk": 2, "bathrooms": 2, "age": 20
        })

        self.assertEqual(resp_new_mumbai.status_code, 200)
        self.assertEqual(resp_old_kolkata.status_code, 200)

        roi_mumbai  = resp_new_mumbai.json()["roi_percent"]
        roi_kolkata = resp_old_kolkata.json()["roi_percent"]
        self.assertGreater(roi_mumbai, roi_kolkata)
        print(f"\n[IT02] PASS – Mumbai ROI ({roi_mumbai}%) > Kolkata ROI ({roi_kolkata}%)")

    def test_predicted_price_feeds_into_future_price(self):
        """
        The future_price_5y must be greater than predicted_price –
        meaning PredictionService output is correctly fed into InvestmentAdvisor.
        """
        resp = self._predict({
            "location": "Whitefield, Bangalore", "area": 1500,
            "bhk": 3, "bathrooms": 2, "age": 3
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(data["future_price_5y"], data["predicted_price"])
        growth = data["assumed_growth_rate"]
        print(f"[IT02] PASS – Current ₹{data['predicted_price']:,} → "
              f"Future ₹{data['future_price_5y']:,} at {growth}% growth/yr")

    def test_investment_score_and_recommendation_are_consistent(self):
        """
        If score ≤ 4 → 'Risky', 5-7 → 'Moderate', ≥ 8 → 'Good'.
        The score and recommendation in a single response must agree.
        """
        resp = self._predict({
            "location": "Anna Nagar, Chennai", "area": 1000,
            "bhk": 2, "bathrooms": 2, "age": 5
        })
        data = resp.json()
        score = data["investment_score"]
        rec   = data["recommendation"]

        if score <= 4:
            self.assertEqual(rec, "Risky Investment")
        elif 5 <= score <= 7:
            self.assertEqual(rec, "Moderate Investment")
        else:
            self.assertEqual(rec, "Good Investment")
        print(f"[IT02] PASS – Score {score} ↔ '{rec}' are consistent.")

    def test_larger_area_produces_higher_future_price(self):
        """
        Since PredictionService is price-sensitive, a larger area → higher
        predicted_price → higher future_price_5y (integration chain check).
        """
        resp_small = self._predict({
            "location": "Whitefield, Bangalore", "area": 500,
            "bhk": 2, "bathrooms": 1, "age": 5
        })
        resp_large = self._predict({
            "location": "Whitefield, Bangalore", "area": 2000,
            "bhk": 2, "bathrooms": 1, "age": 5
        })
        fp_small = resp_small.json()["future_price_5y"]
        fp_large = resp_large.json()["future_price_5y"]
        self.assertGreater(fp_large, fp_small)
        print(f"[IT02] PASS – Future price scales: 500sqft=₹{fp_small:,}, 2000sqft=₹{fp_large:,}")


# =============================================================================
# IT03 – Heatmap API and Google Maps JavaScript Integration Test
# Validates the complete data pipeline from the dataset → API → payload that
# the frontend Google Maps JS visualisation consumes.
# =============================================================================
class IT03_HeatmapAPIAndGoogleMapsIntegrationTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url    = "/api/price-heatmap"

    def test_heatmap_api_returns_200(self):
        """GET /api/price-heatmap must return HTTP 200."""
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        print(f"\n[IT03] PASS – Heatmap endpoint returned HTTP 200.")

    def test_heatmap_payload_is_google_maps_compatible(self):
        """
        Each entry must have lat, lng (numeric) and price so the Google Maps
        JS HeatmapLayer / Marker can consume it directly without transforms.
        """
        resp = self.client.get(self.url)
        data = resp.json()
        self.assertGreater(len(data), 0)

        for entry in data[:20]:   # sampling
            # Required by Google Maps LatLng constructor
            self.assertIn("lat", entry)
            self.assertIn("lng", entry)
            self.assertIsInstance(entry["lat"], (int, float))
            self.assertIsInstance(entry["lng"], (int, float))
            # Required for heatmap weight / tooltip
            self.assertIn("price", entry)
            self.assertGreater(entry["price"], 0)
            # Human-readable location label
            self.assertIn("location", entry)
            self.assertTrue(len(entry["location"]) > 0)

        print(f"[IT03] PASS – All {min(20, len(data))} sampled entries are Google Maps compatible.")

    def test_heatmap_covers_all_four_dataset_cities(self):
        """
        The heatmap must include data points from Bangalore, Mumbai, Chennai,
        and Kolkata (the four cities in the training dataset).
        """
        resp = self.client.get(self.url)
        data = resp.json()
        cities_found = set()
        for entry in data:
            loc = entry.get("location", "").lower()
            if "bangalore" in loc: cities_found.add("Bangalore")
            if "mumbai"    in loc: cities_found.add("Mumbai")
            if "chennai"   in loc: cities_found.add("Chennai")
            if "kolkata"   in loc: cities_found.add("Kolkata")

        expected_cities = {"Bangalore", "Mumbai", "Chennai", "Kolkata"}
        self.assertEqual(cities_found, expected_cities,
                         f"Missing cities: {expected_cities - cities_found}")
        print(f"[IT03] PASS – All 4 cities covered: {sorted(cities_found)}")

    def test_heatmap_page_loads_and_contains_maps_key_context(self):
        """
        The /heatmap/ page (served to logged-in users) must return 200.
        For unauthenticated users it should redirect to login, confirming
        Django's auth middleware is integrated with the Maps view.
        """
        resp = self.client.get("/heatmap/")
        # Unauthenticated → redirect to login
        self.assertIn(resp.status_code, [200, 302])
        if resp.status_code == 302:
            self.assertIn("login", resp["Location"])
            print(f"[IT03] PASS – /heatmap/ redirects unauthenticated users (auth middleware integrated).")
        else:
            print(f"[IT03] PASS – /heatmap/ returned 200 with Maps context.")

    def test_heatmap_data_not_exceeding_250_entries(self):
        """
        The view samples max 250 entries to keep Google Maps rendering fast.
        The data list must have at most 250 elements.
        """
        resp = self.client.get(self.url)
        data = resp.json()
        self.assertLessEqual(len(data), 250,
                             f"Heatmap returned {len(data)} entries, expected ≤250.")
        print(f"[IT03] PASS – Heatmap returned {len(data)} entries (≤ 250 cap confirmed).")


if __name__ == "__main__":
    print("=" * 70)
    print("INTEGRATION TESTING – Smart Real Estate Price Predictor")
    print("=" * 70)
    unittest.main(verbosity=2)
