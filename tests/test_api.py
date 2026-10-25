"""
=============================================================================
API TESTING – Smart Real Estate Price Predictor
Subject: Software Testing & Quality Assurance (ST & QA)
=============================================================================
API01 – Property Price Prediction API Test
API02 – Prediction API Invalid Request Validation Test
API03 – City Price Heatmap API Response Test
=============================================================================
Uses Django's built-in TestClient (no external server needed).
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
from django.urls import reverse


# =============================================================================
# API01 – Property Price Prediction API Test
# Sends a valid POST request to /api/predict-price and verifies the response
# structure, status code, and that all required keys are present.
# =============================================================================
class API01_PredictPriceAPITest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url    = "/api/predict-price"
        self.valid_payload = {
            "location":  "Whitefield, Bangalore",
            "area":      1200,
            "bhk":       3,
            "bathrooms": 2,
            "age":       5
        }

    def test_status_200_for_valid_request(self):
        """Valid payload must return HTTP 200 OK."""
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200,
                         f"Expected 200, got {response.status_code}: {response.content}")
        print(f"\n[API01] PASS – HTTP 200 received for valid prediction request.")

    def test_response_contains_predicted_price(self):
        """Response JSON must include 'predicted_price' key."""
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type="application/json"
        )
        data = response.json()
        self.assertIn("predicted_price", data)
        price = data["predicted_price"]
        self.assertIsInstance(price, int)
        self.assertGreater(price, 0)
        print(f"[API01] PASS – predicted_price present: ₹{price:,}")

    def test_response_contains_investment_fields(self):
        """Response must include all investment advisor fields."""
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type="application/json"
        )
        data = response.json()
        required_keys = [
            "predicted_price", "currency",
            "future_price_5y", "roi_percent",
            "investment_score", "recommendation", "assumed_growth_rate"
        ]
        for key in required_keys:
            self.assertIn(key, data, f"Missing key in API response: '{key}'")
        print(f"[API01] PASS – All required keys present: {required_keys}")

    def test_currency_is_inr(self):
        """The 'currency' field must always be 'INR'."""
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type="application/json"
        )
        data = response.json()
        self.assertEqual(data.get("currency"), "INR")
        print(f"[API01] PASS – Currency is 'INR' as expected.")

    def test_recommendation_is_valid_string(self):
        """The recommendation must be one of the three defined strings."""
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type="application/json"
        )
        data = response.json()
        valid_recs = {"Risky Investment", "Moderate Investment", "Good Investment"}
        self.assertIn(data.get("recommendation"), valid_recs)
        print(f"[API01] PASS – Recommendation is '{data['recommendation']}'")


# =============================================================================
# API02 – Prediction API Invalid Request Validation Test
# Ensures the API returns HTTP 400 for bad/missing inputs and that the
# error body points to the offending field(s).
# =============================================================================
class API02_InvalidRequestValidationTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url    = "/api/predict-price"

    def _post(self, payload):
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json"
        )

    def test_missing_location_returns_400(self):
        """Omitting 'location' must return HTTP 400."""
        payload = {"area": 1200, "bhk": 3, "bathrooms": 2, "age": 5}
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("location", resp.json())
        print(f"\n[API02] PASS – Missing location → 400: {resp.json()}")

    def test_area_too_small_returns_400(self):
        """Area = 50 (below min 100) must return HTTP 400."""
        payload = {
            "location": "Andheri, Mumbai", "area": 50,
            "bhk": 2, "bathrooms": 1, "age": 3
        }
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("area", resp.json())
        print(f"[API02] PASS – Small area → 400: {resp.json()}")

    def test_negative_bhk_returns_400(self):
        """Negative BHK must return HTTP 400."""
        payload = {
            "location": "Whitefield, Bangalore", "area": 1000,
            "bhk": -2, "bathrooms": 1, "age": 5
        }
        resp = self._post(payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("bhk", resp.json())
        print(f"[API02] PASS – Negative BHK → 400: {resp.json()}")

    def test_empty_body_returns_400(self):
        """An empty POST body must return HTTP 400 with field errors."""
        resp = self._post({})
        self.assertEqual(resp.status_code, 400)
        print(f"[API02] PASS – Empty body → 400: {resp.json()}")

    def test_invalid_content_type_returns_400(self):
        """Sending plain text instead of JSON must be gracefully rejected."""
        resp = self.client.post(self.url, data="not json", content_type="text/plain")
        # DRF returns 400 or 415 for non-parseable input
        self.assertIn(resp.status_code, [400, 415])
        print(f"[API02] PASS – Plain text body → HTTP {resp.status_code}")


# =============================================================================
# API03 – City Price Heatmap API Response Test
# Sends a GET request to /api/price-heatmap and verifies that the response
# is a list of location objects with the expected schema.
# =============================================================================
class API03_PriceHeatmapAPITest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url    = "/api/price-heatmap"

    def test_heatmap_returns_200(self):
        """GET /api/price-heatmap must return HTTP 200."""
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        print(f"\n[API03] PASS – Heatmap API returned HTTP 200.")

    def test_heatmap_response_is_list(self):
        """Response body must be a JSON array."""
        resp = self.client.get(self.url)
        data = resp.json()
        self.assertIsInstance(data, list)
        print(f"[API03] PASS – Response is a list with {len(data)} entries.")

    def test_heatmap_entries_have_required_keys(self):
        """Each entry must have: location, lat, lng, price."""
        resp = self.client.get(self.url)
        data = resp.json()
        self.assertGreater(len(data), 0, "Heatmap returned 0 entries.")
        required = {"location", "lat", "lng", "price"}
        for i, entry in enumerate(data[:5]):   # Check first 5 entries
            missing = required - set(entry.keys())
            self.assertEqual(len(missing), 0,
                             f"Entry {i} missing keys: {missing}")
        print(f"[API03] PASS – Required keys present in all checked entries.")

    def test_heatmap_lat_lng_are_numeric(self):
        """lat and lng values must be floats within valid geographic ranges."""
        resp = self.client.get(self.url)
        data = resp.json()
        for entry in data[:10]:
            self.assertIsInstance(entry["lat"], (int, float))
            self.assertIsInstance(entry["lng"], (int, float))
            # India bounds: lat 6°–37°N, lng 68°–98°E
            self.assertTrue(6 <= entry["lat"] <= 37,
                            f"lat out of range: {entry['lat']}")
            self.assertTrue(68 <= entry["lng"] <= 98,
                            f"lng out of range: {entry['lng']}")
        print(f"[API03] PASS – Lat/lng values are valid geographic coordinates.")

    def test_heatmap_price_is_positive(self):
        """price in each heatmap entry must be a positive number."""
        resp = self.client.get(self.url)
        data = resp.json()
        for entry in data[:10]:
            self.assertGreater(entry["price"], 0)
        print(f"[API03] PASS – All sampled heatmap prices are positive.")


if __name__ == "__main__":
    print("=" * 70)
    print("API TESTING – Smart Real Estate Price Predictor")
    print("=" * 70)
    unittest.main(verbosity=2)
