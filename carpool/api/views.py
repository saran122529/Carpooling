# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from website.models import ContactUs, Customer, Driver
from .serializers import ContactUsSerializer, CustomerRegistrationSerializer, DriverRegistrationSerializer


class CustomerRegistrationView(APIView):
     def get(self, request):
         customers = Customer.objects.all()
         serializer = CustomerRegistrationSerializer(customers, many=True)
         return Response(serializer.data)
    
     def post(self, request):
         serializer = CustomerRegistrationSerializer(data=request.data)
         if serializer.is_valid():
             serializer.save()
             return Response(serializer.data, status=status.HTTP_201_CREATED)
         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class DriverRegistrationView(APIView):
     def get(self, request):
         drivers = Driver.objects.all()
         serializer = DriverRegistrationSerializer(drivers, many=True)
         return Response(serializer.data)
    
     def post(self, request):
         serializer = DriverRegistrationSerializer(data=request.data)
         if serializer.is_valid():
             serializer.save()
             return Response(serializer.data, status=status.HTTP_201_CREATED)
         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ContactUsView(APIView):
     def get(self, request):
         contacts = ContactUs.objects.all()
         serializer = ContactUsSerializer(contacts, many=True)
         return Response(serializer.data)
    
     def post(self, request):
         serializer = ContactUsSerializer(data=request.data)
         if serializer.is_valid():
             serializer.save()
             return Response(serializer.data, status=status.HTTP_201_CREATED)
         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

