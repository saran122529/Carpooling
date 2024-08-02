# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from website.models import Customer, Driver, ContactUs

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['usern', 'fname', 'email', 'password', 'mobile', 'gender', 'address', 'city', 'state', 'college', 'degree', 'field_of_study', 'graduation_year', 'languages', 'current_status', 'company_name', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(username=validated_data['usern'], email=validated_data['email'])
        user.set_password(password)  # This will hash the password
        user.save()
        customer = Customer.objects.create(usern=user.username, fname=validated_data['fname'], email=validated_data['email'],
                                           mobile=validated_data['mobile'], gender=validated_data['gender'],
                                           address=validated_data['address'], city=validated_data['city'], state=validated_data['state'], 
                                           college=validated_data['college'], degree=validated_data['degree'], field_of_study=validated_data['field_of_study'], 
                                           graduation_year=validated_data['graduation_year'], languages=validated_data['languages'], current_status=validated_data['current_status'], 
                                           company_name=validated_data['company_name'], role=validated_data['role'])
        return customer

class DriverRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['usern', 'fname', 'email', 'mobile', 'address', 'gender', 'state', 'city', 'password', 'role', 'year_of_experience', 'languages_spoken', 'services', 'description']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(username=validated_data['usern'], email=validated_data['email'])
        user.set_password(password)  # This will hash the password
        user.save()
        driver = Driver.objects.create(usern=user.username, fname=validated_data['fname'], email=validated_data['email'],
                                       mobile=validated_data['mobile'], address=validated_data['address'],
                                       gender=validated_data['gender'], state=validated_data['state'], city=validated_data['city'], 
                                       role=validated_data['role'], year_of_experience=validated_data['year_of_experience'], 
                                       languages_spoken=validated_data['languages_spoken'], services=validated_data['services'], 
                                       description=validated_data['description'])
        return driver
class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'

# class CustomerRegistrationSerializer(serializers.ModelSerializer):
#      class Meta:
#         model = Customer
#         fields = '__all__'  # You might want to specify fields explicitly

# class DriverRegistrationSerializer(serializers.ModelSerializer):
#      class Meta:
#         model = Driver
#         fields = '__all__'  # You might want to specify fields explicitly