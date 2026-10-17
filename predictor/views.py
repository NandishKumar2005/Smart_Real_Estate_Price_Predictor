import os
import json
import secrets
import requests as http_requests

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.urls import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import PredictionRequestSerializer
from .models import PredictionHistory, PropertyLocation
from services.investment_advisor import InvestmentAdvisor
from services.prediction_service import PredictionService

prediction_service = PredictionService()
investment_advisor = InvestmentAdvisor()

# ---------------------------------------------------------------------------
# Google OAuth2 helpers
# ---------------------------------------------------------------------------
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_SCOPE = "openid email profile"


def _google_redirect_uri(request):
    """Build the absolute callback URL."""
    return request.build_absolute_uri(reverse('google-oauth-callback'))


class GoogleOAuthInitView(View):
    def get(self, request):
        state = secrets.token_urlsafe(16)
        request.session['google_oauth_state'] = state

        params = {
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "redirect_uri": _google_redirect_uri(request),
            "response_type": "code",
            "scope": GOOGLE_SCOPE,
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }
        from urllib.parse import urlencode
        url = GOOGLE_AUTH_URL + "?" + urlencode(params)
        return redirect(url)


class GoogleOAuthCallbackView(View):
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        stored_state = request.session.pop('google_oauth_state', None)

        if not code or state != stored_state:
            messages.error(request, 'Google sign-in failed. Please try again.')
            return redirect('login')

        # Exchange code for tokens
        token_resp = http_requests.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": _google_redirect_uri(request),
            "grant_type": "authorization_code",
        })

        if token_resp.status_code != 200:
            messages.error(request, 'Failed to obtain token from Google.')
            return redirect('login')

        access_token = token_resp.json().get('access_token')

        # Fetch user info
        userinfo_resp = http_requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if userinfo_resp.status_code != 200:
            messages.error(request, 'Failed to fetch user info from Google.')
            return redirect('login')

        userinfo = userinfo_resp.json()
        email = userinfo.get('email')
        name = userinfo.get('name', email.split('@')[0] if email else 'user')
        # Use the Google sub as a unique, safe username
        google_sub = userinfo.get('sub', '')
        username = f"google_{google_sub}"

        if not email:
            messages.error(request, 'Could not retrieve email from Google.')
            return redirect('login')

        # Get or create the Django user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'first_name': name}
        )
        if not created:
            # Keep email/name in sync
            user.email = email
            user.first_name = name
            user.save()

        login(request, user)
        messages.success(request, f'Welcome, {name}!')
        return redirect('home')


# ---------------------------------------------------------------------------
# API Views
# ---------------------------------------------------------------------------

class PriceHeatmapAPIView(APIView):
    def get(self, request):
        import pandas as pd
        try:
            dataset_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'ml', 'merged_files.csv'
            )
            df = pd.read_csv(dataset_path)

            city_coords = {
                'Bangalore': {'lat': 12.9716, 'lon': 77.5946},
                'Mumbai':    {'lat': 19.0760, 'lon': 72.8777},
                'Chennai':   {'lat': 13.0827, 'lon': 80.2707},
                'Kolkata':   {'lat': 22.5726, 'lon': 88.3639}
            }

            grouped = df.groupby(['City', 'Location'])['Price'].mean().reset_index()
            if len(grouped) > 250:
                grouped = grouped.sample(n=250, random_state=42)

            data = []
            for _, row in grouped.iterrows():
                city = row['City'].strip()
                if city in city_coords:
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
            locations = PropertyLocation.objects.all()
            data = [
                {"location": loc.location_name, "lat": loc.latitude,
                 "lng": loc.longitude, "price": loc.avg_price}
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
                return Response(
                    {'predicted_price': price, 'currency': 'INR', **investment_data},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Page Views
# ---------------------------------------------------------------------------

class HomeView(TemplateView):
    template_name = 'home.html'


class PredictView(LoginRequiredMixin, TemplateView):
    template_name = 'predict.html'

    def get_context_data(self, **kwargs):
        import joblib
        context = super().get_context_data(**kwargs)
        locations_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ml', 'locations.pkl'
        )
        try:
            context['locations'] = joblib.load(locations_path)
        except Exception:
            context['locations'] = []
        return context


class ResultView(LoginRequiredMixin, TemplateView):
    template_name = 'result.html'


class HeatmapView(LoginRequiredMixin, TemplateView):
    template_name = 'heatmap.html'


class HistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['history'] = PredictionHistory.objects.filter(
            user=self.request.user
        ).order_by('-timestamp')
        return context


# ---------------------------------------------------------------------------
# Auth Views
# ---------------------------------------------------------------------------

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'auth/login.html')

    def post(self, request):
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        messages.error(request, 'Invalid credentials')
        return redirect('login')


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'auth/register.html')

    def post(self, request):
        u = request.POST.get('username')
        p = request.POST.get('password')
        if not User.objects.filter(username=u).exists():
            user = User.objects.create_user(username=u, password=p)
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('home')
        messages.error(request, 'Username already taken')
        return redirect('register')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')


class DebugEnvAPIView(APIView):
    def get(self, request):
        keys = list(os.environ.keys())
        keys_summary = {key: "Set" if os.environ.get(key) else "Empty" for key in keys}
        return Response({
            "keys": keys_summary,
            "has_database_url": "DATABASE_URL" in os.environ,
            "has_postgres_url": "POSTGRES_URL" in os.environ,
            "google_oauth_configured": bool(settings.GOOGLE_OAUTH_CLIENT_ID),
        })
