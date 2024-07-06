# urls.py
from django.urls import path
from api import views

urlpatterns = [
    path('api/contact/', views.ContactUsView.as_view(), name='contact-us'),
    path('api/register/customer/', views.CustomerRegistrationView.as_view(), name='customer-register'),
    path('api/register/driver/', views.DriverRegistrationView.as_view(), name='driver-register'),
]
