from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('predict/', views.PredictView.as_view(), name='predict'),
    path('result/', views.ResultView.as_view(), name='result'),
    path('heatmap/', views.HeatmapView.as_view(), name='heatmap'),
    path('dashboard/', views.HistoryView.as_view(), name='history'),

    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Google OAuth2
    path('auth/google/', views.GoogleOAuthInitView.as_view(), name='google-oauth-init'),
    path('auth/google/callback/', views.GoogleOAuthCallbackView.as_view(), name='google-oauth-callback'),

    path('api/predict-price', views.PredictPriceAPIView.as_view(), name='api-predict-price'),
    path('api/price-heatmap', views.PriceHeatmapAPIView.as_view(), name='api-price-heatmap'),
    path('api/debug-env', views.DebugEnvAPIView.as_view(), name='api-debug-env'),
]
