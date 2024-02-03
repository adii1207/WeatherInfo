from django.urls import path, include
from weatherReportApp.views import CustomTokenObtainPairView

weaterReportUrls = include("weatherReportApp.urls")

urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('weather-data/', weaterReportUrls),
]
