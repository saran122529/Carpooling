from django.urls import path
from website.views import Cars
from website import views
from .views import service_create  # Import the service_create function
from .views import service_create, service_detail, payment, payment_verification



urlpatterns=[
    path('',views.home, name="home"),
    path('login/', views.LoginUser, name="login"),
    path('page/<str:username>/', views.page, name='page'),
    path('delete-schedule/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('register/', views.Register, name="register"),
    path('contact/', views.Contactus, name="contact"),
    path('dashboard/', views.dash, name="dashboard"),
    path('allcars/', views.Cars, name="allcars"),
    path('addmycar/', views.Addcar, name="addmycar"),
    path('mycar_list/', views.MyCarList, name="mycar_list"),
    path('changepassword/', views.Change, name="changepassword"),
    path('searchmycar/', views.Search, name="searchmycar"),
    path('cardetails/<int:car_id>/', views.Cardetails, name="cardetails"),
    path('bookedcar/<int:car_id>/',views.Booked,name="bookedcar"),
    path('mybookings/', views.MyBookings, name="mybookings"),
    path('myaccount', views.MyAccount,name="myaccount"),
    path('customerbookings/', views.CustomerBookings, name="customerbookings"),
    path('logout/',views.logout_user, name="logout"),
    path('bookings/', views.bookings_view, name='bookings'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('service/', views.service_view, name='service'),
    path('testimonial/', views.testimonial_view, name='testimonial'),
    path('service/create/', service_create, name='service_create'),
    path('service/<int:pk>/', views.service_detail, name='service_detail'),
    path('payment/', payment, name='payment'),
    path('payment/verification/', payment_verification, name='payment_verification'),

    

]