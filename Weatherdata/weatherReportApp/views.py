from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from rest_framework.throttling import UserRateThrottle
from datetime import datetime, timedelta


class UserRegistrationView(APIView):
    def post(self, request):
        """
        Process a POST request with user registration data and return the appropriate response.

        :param request: The request object containing user registration data.
        :return: Response with user data and appropriate status code.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

def getWeatherData(latitude, longitude):
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Number of days into the future for the forecast
    days_into_future = 3

    # Calculate the end date based on the current date and the number of days into the future
    end_date = (datetime.utcnow() + timedelta(days=days_into_future)).isoformat()
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        # "past_days": pastDays,
        "hourly": [
            "temperature_2m",
            "precipitation",
            "cloud_cover",
            "cloud_cover_low",
            "cloud_cover_mid",
            "cloud_cover_high",
        ],
        "start": "now",
        "end": end_date,
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
    # print(f"Elevation {response.Elevation()} m asl")
    # print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    # print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(2).ValuesAsNumpy()
    hourly_cloud_cover_low = hourly.Variables(3).ValuesAsNumpy()
    hourly_cloud_cover_mid = hourly.Variables(4).ValuesAsNumpy()
    hourly_cloud_cover_high = hourly.Variables(5).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s"),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s") - pd.Timedelta(seconds=1),
            freq=pd.Timedelta(seconds=hourly.Interval()),
        )
    }
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
    hourly_data["cloud_cover_mid"] = hourly_cloud_cover_mid
    hourly_data["cloud_cover_high"] = hourly_cloud_cover_high

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    return hourly_dataframe


def sendMail(weatherData, emailId):
    # convert the weather data to csv format to be attached in email
    csv_data = weatherData.to_csv(index=False)

    # Attach the CSV file to the email
    attachment = ("hourly_data.csv", csv_data, "text/csv")

    # Email settings
    subject = "Hourly Weather Data"
    message = "Hourly weather data attached."
    from_email = "adityakanouje@gmail.com"
    to_email = [emailId]

    # Create and send the email
    email = EmailMessage(subject, message, from_email, to_email)
    email.attach(*attachment)  # Attach the CSV file
    email.send()


class WeatherHistoricData(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    def get(self, request, *args, **kwargs):
        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")
        if latitude is None or longitude is None:
            return Response(
                {"message": "latitude, longitude and past_days are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # get the weather data using latitude, longitude and pastDays
        hourly_dataframe = getWeatherData(latitude, longitude)

        # send email to the user
        emailId = User.objects.get(username=request.user.username).email
        sendMail(hourly_dataframe, emailId)
        return Response(
            {
                "message": "Check Your Email for the weather data",
                "data": hourly_dataframe,
            },
            status=status.HTTP_200_OK,
        )
