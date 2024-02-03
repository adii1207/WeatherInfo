from django.urls import path
from .views import UserRegistrationView, WeatherHistoricData

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('report/', WeatherHistoricData.as_view(), name='weather-report-data'),
]