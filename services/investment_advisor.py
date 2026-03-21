class InvestmentAdvisor:
    def __init__(self, years=5):
        self.years = years

    def analyze_investment(self, current_price, property_age=0, location=""):
        """
        Calculates ROI based on property age and specific city growth rates.
        """
        # Base growth rate
        growth_rate = 0.07  # Default 7%
        
        # City-specific growth adjustments based on your dataset
        location_lower = location.lower()
        if "mumbai" in location_lower:
            growth_rate = 0.09  # Mumbai usually has high appreciation
        elif "bangalore" in location_lower:
            growth_rate = 0.08  # Tech hub growth
        elif "chennai" in location_lower:
            growth_rate = 0.06  # Stable growth
        elif "kolkata" in location_lower:
            growth_rate = 0.05  # Slower appreciation
            
        # Adjust growth rate based on Age
        if property_age > 15:
            growth_rate -= 0.03 
        elif property_age < 3:
            growth_rate += 0.02 
            
        # 1. Expected Future Price Formula
        future_price_5y = current_price * ((1 + growth_rate) ** self.years)
        
        # 2. ROI Calculation
        roi_percent = ((future_price_5y - current_price) / current_price) * 100
        
        # 3. Dynamic Investment Score
        if roi_percent < 25:
            investment_score = 4 # Risky
        elif 25 <= roi_percent <= 35:
            investment_score = 6 # Moderate
        else:
            investment_score = 9 # Good
            
        # 4. Recommendation String
        if investment_score <= 4:
            recommendation = "Risky Investment"
        elif 5 <= investment_score <= 7:
            recommendation = "Moderate Investment"
        else:
            recommendation = "Good Investment"
            
        return {
            "future_price_5y": int(future_price_5y),
            "roi_percent": round(roi_percent, 1),
            "investment_score": investment_score,
            "recommendation": recommendation,
            "assumed_growth_rate": round(growth_rate * 100, 1)
        }
