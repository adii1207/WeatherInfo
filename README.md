# WeatherInfo
Weather Info is a django app through which after user registration , the user can fetch weather information.


- Clone the repository
- in the terminal navigate to the folder Weatherdata folder
- Run the following docker commands
   - docker build --tag django-app .
   - docker run --publish 8000:8000 django-app
- api will be accesible at "http://127.0.0.1:8000/"
- register a user using the POST api "http://127.0.0.1:8000/weather-data/register/" with the payload { "username":"testuser1","password":"1system@", "email":"abc@yopmail.com"}, add the username ,password and email accordingly.
- get the jwt token using the POST api "http://127.0.0.1:8000/api/token/" with the payload { "username":"testuser1","password":"1system@"}, use the username and password as per the given username in above api
- use the "access_token" generated from "http://127.0.0.1:8000/api/token/" and hit the GET api "http://127.0.0.1:8000/weather-data/report/?latitude=52.52&longitude=13.41", You can change the values of latitude , longitude
  

  The api's mentioned has a ratelimit of 10 api call per day and the concept I have used is throtlling which comes inbuilt with django
  the api "http://127.0.0.1:8000/weather-data/report/?latitude=52.52&longitude=13.41" will give the weather forecast for 3 days in response and also in email with which the user got registered
