from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PredictionRequestSerializer
from .models import PredictionHistory, PropertyLocation
from services.investment_advisor import InvestmentAdvisor
from services.prediction_service import PredictionService

prediction_service = PredictionService()
investment_advisor = InvestmentAdvisor()

class PriceHeatmapAPIView(APIView):
    def get(self, request):
        import pandas as pd
        import os
        import random
        # Optional: You can cache this or use a more optimal storage in a large prod app
        try:
            dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml', 'merged_files.csv')
            df = pd.read_csv(dataset_path)
            
            # Since the dataset doesn't have lat/long hardcoded inside it currently, and realtime geocoding 30,000 points 
            # via Nominatim is impossible due to rate limits, we'll provide approximate coordinates of the 4 major cities
            # mapped to a realistic jitter to form a "heatmap" visual cluster since user wants multiple cities.
            
            city_coords = {
                'Bangalore': {'lat': 12.9716, 'lon': 77.5946},
                'Mumbai': {'lat': 19.0760, 'lon': 72.8777},
                'Chennai': {'lat': 13.0827, 'lon': 80.2707},
                'Kolkata': {'lat': 22.5726, 'lon': 88.3639}
            }
            
            # Group by location, take average price
            grouped = df.groupby(['City', 'Location'])['Price'].mean().reset_index()
            
            # Downsample visually so we don't crash leaflet by dumping 2k points at once
            if len(grouped) > 250:
                grouped = grouped.sample(n=250, random_state=42)
                
            data = []
            for _, row in grouped.iterrows():
                city = row['City'].strip()
                if city in city_coords:
                    # add small jitter offset based on index hash so points don't perfectly overlap
                    jitter_lat = (hash(row['Location']) % 100) / 1000.0 - 0.05
                    jitter_lon = (hash(row['Location']) % 100) / 1000.0 - 0.05
                    
                    data.append({
                        "location": f"{row['Location']}, {city}",
                        "lat": city_coords[city]['lat'] + jitter_lat,
                        "lng": city_coords[city]['lon'] + jitter_lon,
                        "price": row['Price']
                    })

            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Fallback to the original model if file reading fails
            locations = PropertyLocation.objects.all()
            data = [
                {
                    "location": loc.location_name,
                    "lat": loc.latitude,
                    "lng": loc.longitude,
                    "price": loc.avg_price
                }
                for loc in locations
            ]
            return Response(data, status=status.HTTP_200_OK)

class PredictPriceAPIView(APIView):
    def post(self, request):
        serializer = PredictionRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                data = serializer.validated_data
                price = prediction_service.predict(
                    data['location'], data['area'], data['bhk'], 
                    data['bathrooms'], data['age']
                )
                
                investment_data = investment_advisor.analyze_investment(
                    price, 
                    property_age=data.get('age', 0), 
                    location=data.get('location', "")
                )
                
                if request.user.is_authenticated:
                    PredictionHistory.objects.create(
                        user=request.user,
                        location=data['location'],
                        area=data['area'],
                        bhk=data['bhk'],
                        bathrooms=data['bathrooms'],
                        age=data['age'],
                        predicted_price=price
                    )
                
                response_data = {
                    'predicted_price': price,
                    'currency': 'INR',
                    **investment_data
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HomeView(TemplateView):
    template_name = 'home.html'

class PredictView(TemplateView):
    template_name = 'predict.html'
    
    def get_context_data(self, **kwargs):
        import joblib
        import os
        context = super().get_context_data(**kwargs)
        locations_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml', 'locations.pkl')
        try:
            context['locations'] = joblib.load(locations_path)
        except Exception:
            context['locations'] = []
        return context

class ResultView(TemplateView):
    template_name = 'result.html'

class HeatmapView(TemplateView):
    template_name = 'heatmap.html'

class HistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['history'] = PredictionHistory.objects.filter(user=self.request.user).order_by('-timestamp')
        return context

class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')
    
    def post(self, request):
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        messages.error(request, 'Invalid credentials')
        return redirect('login')

class RegisterView(View):
    def get(self, request):
        return render(request, 'auth/register.html')
        
    def post(self, request):
        u = request.POST.get('username')
        p = request.POST.get('password')
        if not User.objects.filter(username=u).exists():
            user = User.objects.create_user(username=u, password=p)
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        messages.error(request, 'Username already taken')
        return redirect('register')

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')
