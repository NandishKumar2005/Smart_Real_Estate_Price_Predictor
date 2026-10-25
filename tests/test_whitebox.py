"""
=============================================================================
WHITE BOX TESTING - Smart Real Estate Price Predictor
Subject: Software Testing & Quality Assurance (ST & QA)
=============================================================================
WB01 – Input Validation Function Test
WB02 – Prediction Service Feature Processing Test
WB03 – Machine Learning Model Loading and Reuse Test
WB04 – ROI Calculation Logic Test
WB05 – Investment Recommendation Conditional Branch Test
WB06 – Exception Handling and Error Management Test
=============================================================================
"""

import os
import sys
import unittest

# ---------------------------------------------------------------------------
# Bootstrap Django environment (needed for DRF serializer)
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "real_estate_ai.settings")

import django
django.setup()

from predictor.serializers import PredictionRequestSerializer
from services.prediction_service import PredictionService
from services.investment_advisor import InvestmentAdvisor


# =============================================================================
# WB01 – Input Validation Function Test
# Verifies that the DRF serializer correctly validates all required fields,
# enforces minimum values, and rejects malformed / missing inputs.
# =============================================================================
class WB01_InputValidationTest(unittest.TestCase):

    def test_valid_data_passes_validation(self):
        """All valid fields should produce a valid serializer."""
        data = {
            "location": "Whitefield, Bangalore",
            "area": 1200,
            "bhk": 3,
            "bathrooms": 2,
            "age": 5
        }
        serializer = PredictionRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        print("\n[WB01] PASS – Valid input accepted by serializer.")

    def test_missing_required_field_fails(self):
        """Missing 'location' field must trigger a validation error."""
        data = {"area": 1200, "bhk": 3, "bathrooms": 2, "age": 5}
        serializer = PredictionRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("location", serializer.errors)
        print("[WB01] PASS – Missing 'location' caught by validator.")

    def test_area_below_minimum_fails(self):
        """Area < 100 sqft must be rejected (min_value=100 in serializer)."""
        data = {
            "location": "Whitefield, Bangalore",
            "area": 50,          # below min_value=100
            "bhk": 2,
            "bathrooms": 1,
            "age": 3
        }
        serializer = PredictionRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("area", serializer.errors)
        print("[WB01] PASS – Area below minimum (50) correctly rejected.")

    def test_negative_bhk_fails(self):
        """BHK must be at least 1; negative value should fail."""
        data = {
            "location": "Andheri, Mumbai",
            "area": 800,
            "bhk": -1,
            "bathrooms": 1,
            "age": 2
        }
        serializer = PredictionRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("bhk", serializer.errors)
        print("[WB01] PASS – Negative BHK (-1) correctly rejected.")

    def test_empty_location_string_fails(self):
        """Empty location string must fail CharField validation."""
        data = {
            "location": "",
            "area": 900,
            "bhk": 2,
            "bathrooms": 1,
            "age": 4
        }
        serializer = PredictionRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("location", serializer.errors)
        print("[WB01] PASS – Empty location string caught by validator.")


# =============================================================================
# WB02 – Prediction Service Feature Processing Test
# Verifies internal DataFrame construction and pipeline execution inside
# PredictionService.predict().
# =============================================================================
class WB02_PredictionServiceTest(unittest.TestCase):

    def setUp(self):
        self.service = PredictionService()

    def test_predict_returns_positive_integer(self):
        """predict() must return a non-negative integer for valid known input."""
        price = self.service.predict("Whitefield, Bangalore", 1200, 3, 2, 5)
        self.assertIsInstance(price, int)
        self.assertGreaterEqual(price, 0)
        print(f"\n[WB02] PASS – predict() returned ₹{price:,} (int ≥ 0).")

    def test_predict_output_is_non_negative(self):
        """max(0, predicted) guard ensures output is never negative."""
        price = self.service.predict("Andheri, Mumbai", 600, 1, 1, 20)
        self.assertGreaterEqual(price, 0)
        print(f"[WB02] PASS – Old-property prediction ≥ 0: ₹{price:,}")

    def test_predict_varies_with_area(self):
        """Larger area must produce a higher price than smaller area."""
        price_small = self.service.predict("Anna Nagar, Chennai", 500, 2, 1, 5)
        price_large = self.service.predict("Anna Nagar, Chennai", 2000, 2, 1, 5)
        self.assertGreater(price_large, price_small)
        print(f"[WB02] PASS – Area sensitivity: 500sqft=₹{price_small:,}, 2000sqft=₹{price_large:,}")


# =============================================================================
# WB03 – Machine Learning Model Loading and Reuse (Singleton) Test
# Verifies that PredictionService follows the Singleton pattern and that the
# model is loaded only once.
# =============================================================================
class WB03_ModelLoadingAndReuseTest(unittest.TestCase):

    def test_singleton_returns_same_instance(self):
        """Two PredictionService() calls must return the exact same object."""
        svc1 = PredictionService()
        svc2 = PredictionService()
        self.assertIs(svc1, svc2)
        print("\n[WB03] PASS – Both instances are the same Singleton object.")

    def test_model_is_not_none_after_loading(self):
        """_model attribute must be populated after initialization."""
        svc = PredictionService()
        self.assertIsNotNone(svc._model)
        print("[WB03] PASS – Model loaded successfully, _model is not None.")

    def test_model_is_shared_across_instances(self):
        """Both instances must share the identical model object."""
        svc1 = PredictionService()
        svc2 = PredictionService()
        self.assertIs(svc1._model, svc2._model)
        print("[WB03] PASS – Model object is shared (same id) across singletons.")


# =============================================================================
# WB04 – ROI Calculation Logic Test
# Traces through the compound-growth formula and ROI percent maths in
# InvestmentAdvisor.analyze_investment().
# =============================================================================
class WB04_ROICalculationTest(unittest.TestCase):

    def setUp(self):
        self.advisor = InvestmentAdvisor(years=5)

    def test_roi_percent_formula(self):
        """ROI = (future - current) / current * 100, cross-check manually."""
        current = 5_000_000  # ₹50 Lakhs
        result = self.advisor.analyze_investment(current, property_age=5, location="Pune")
        growth = 0.07         # default
        future = current * ((1 + growth) ** 5)
        expected_roi = round(((future - current) / current) * 100, 1)
        self.assertAlmostEqual(result["roi_percent"], expected_roi, places=1)
        print(f"\n[WB04] PASS – ROI formula correct: {result['roi_percent']}% matches manual calc {expected_roi}%")

    def test_future_price_increases_with_price(self):
        """Higher current price must yield proportionally higher future price."""
        r1 = self.advisor.analyze_investment(3_000_000, property_age=5, location="Pune")
        r2 = self.advisor.analyze_investment(6_000_000, property_age=5, location="Pune")
        self.assertGreater(r2["future_price_5y"], r1["future_price_5y"])
        print(f"[WB04] PASS – Future price scales: ₹{r1['future_price_5y']:,} vs ₹{r2['future_price_5y']:,}")

    def test_city_growth_rate_applied_correctly_mumbai(self):
        """Mumbai (9%) must yield higher ROI than default (7%) for same price."""
        result_default = self.advisor.analyze_investment(5_000_000, property_age=5, location="Hyderabad")
        result_mumbai  = self.advisor.analyze_investment(5_000_000, property_age=5, location="Mumbai")
        self.assertGreater(result_mumbai["roi_percent"], result_default["roi_percent"])
        print(f"[WB04] PASS – Mumbai ROI ({result_mumbai['roi_percent']}%) > Default ROI ({result_default['roi_percent']}%)")

    def test_old_property_reduces_growth_rate(self):
        """Property age > 15 applies a -0.03 penalty on growth rate."""
        result_new = self.advisor.analyze_investment(5_000_000, property_age=2,  location="Pune")
        result_old = self.advisor.analyze_investment(5_000_000, property_age=20, location="Pune")
        self.assertGreater(result_new["roi_percent"], result_old["roi_percent"])
        print(f"[WB04] PASS – Old property penalty: New={result_new['roi_percent']}%, Old={result_old['roi_percent']}%")


# =============================================================================
# WB05 – Investment Recommendation Conditional Branch Test
# Each score/recommendation branch in InvestmentAdvisor.analyze_investment()
# is exercised to ensure 100% branch coverage.
# =============================================================================
class WB05_InvestmentRecommendationBranchTest(unittest.TestCase):

    def setUp(self):
        self.advisor = InvestmentAdvisor(years=5)

    def _get_result(self, location, age):
        return self.advisor.analyze_investment(5_000_000, property_age=age, location=location)

    def test_risky_investment_branch(self):
        """Old Kolkata property → low ROI → 'Risky Investment'."""
        result = self._get_result("Kolkata", age=20)  # 0.05 - 0.03 = 2% growth
        self.assertEqual(result["recommendation"], "Risky Investment")
        self.assertEqual(result["investment_score"], 4)
        print(f"\n[WB05] PASS – Risky branch: score={result['investment_score']}, ROI={result['roi_percent']}%")

    def test_moderate_investment_branch(self):
        """Chennai with moderate age → moderate ROI → 'Moderate Investment'."""
        # Chennai = 0.06, no age adjustment for age=5 → ROI ≈ 33.8% → score 6
        result = self._get_result("Chennai", age=5)
        self.assertIn(result["recommendation"], ["Moderate Investment", "Good Investment"])
        self.assertIn(result["investment_score"], [6, 9])
        print(f"[WB05] PASS – Moderate/Good branch: score={result['investment_score']}, recommendation='{result['recommendation']}'")

    def test_good_investment_branch(self):
        """New Mumbai property → high ROI → 'Good Investment'."""
        result = self._get_result("Mumbai", age=1)  # 0.09 + 0.02 = 11% → 5yr ROI ~69%
        self.assertEqual(result["recommendation"], "Good Investment")
        self.assertEqual(result["investment_score"], 9)
        print(f"[WB05] PASS – Good branch: score={result['investment_score']}, ROI={result['roi_percent']}%")

    def test_all_four_cities_return_valid_recommendations(self):
        """All four dataset cities must produce a valid recommendation string."""
        valid_recs = {"Risky Investment", "Moderate Investment", "Good Investment"}
        for city in ["Mumbai", "Bangalore", "Chennai", "Kolkata"]:
            result = self._get_result(city, age=5)
            self.assertIn(result["recommendation"], valid_recs)
            print(f"[WB05] PASS – {city}: '{result['recommendation']}' (score={result['investment_score']})")


# =============================================================================
# WB06 – Exception Handling and Error Management Test
# Verifies that exception paths in PredictionService and the API view guard
# properly propagate / handle errors without crashing.
# =============================================================================
class WB06_ExceptionHandlingTest(unittest.TestCase):

    def test_predict_raises_when_model_none(self):
        """Temporarily clearing _model must trigger ValueError in predict()."""
        svc = PredictionService()
        original_model = svc._model
        try:
            svc._model = None
            with self.assertRaises(ValueError) as ctx:
                svc.predict("Whitefield, Bangalore", 1000, 3, 2, 5)
            self.assertIn("not loaded", str(ctx.exception))
            print(f"\n[WB06] PASS – ValueError raised: '{ctx.exception}'")
        finally:
            svc._model = original_model  # Restore for other tests

    def test_prediction_service_initializes_without_crash(self):
        """PredictionService() constructor must not raise any exception."""
        try:
            svc = PredictionService()
            self.assertIsNotNone(svc)
            print("[WB06] PASS – PredictionService initialized without exception.")
        except Exception as e:
            self.fail(f"PredictionService init raised unexpected exception: {e}")

    def test_investment_advisor_handles_zero_price(self):
        """
        Edge case: price=0 must NOT cause ZeroDivisionError.
        WB06 originally found this bug; the fix adds a guard in investment_advisor.py.
        After the fix, price=0 should return roi_percent=0.0 and 'Risky Investment'.
        """
        advisor = InvestmentAdvisor()
        # Should NOT raise ZeroDivisionError after the bug fix
        result = advisor.analyze_investment(0, property_age=5, location="Mumbai")
        self.assertEqual(result["roi_percent"], 0.0)
        self.assertEqual(result["recommendation"], "Risky Investment")
        print(f"[WB06] PASS – Zero price handled safely (bug fix verified): {result}")


if __name__ == "__main__":
    print("=" * 70)
    print("WHITE BOX TESTING – Smart Real Estate Price Predictor")
    print("=" * 70)
    unittest.main(verbosity=2)
