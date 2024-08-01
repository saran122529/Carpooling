from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
# import mysql.connector as sql
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from requests import request
from django.contrib.auth.hashers import make_password
from website.models import Customer, Mycar, ContactUs, Booking, Driver, CalendarData, DeletedSchedule, Service
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CalendarData  # Import your CalendarData model
from django.contrib import messages
from django.db.models import Max
import base64
from django.core.files.base import ContentFile
import razorpay
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
import hmac
import hashlib
from datetime import datetime, timedelta
from .models import Service, CalendarData


# Create your views here.
# Home page
def home(request):
    return render(request, "home.html")


# Function to help login the user and open dashboard
def LoginUser(request):
    if request.method == "GET":
        return render(request, "login.html")

    if request.method == "POST":
        usern = request.POST['usern']
        password = request.POST['password']

        try:
            user = authenticate(username=usern, password=password)
            if user is not None:
                login(request, user)

                # Check if the user is a Customer
                if Customer.objects.filter(usern=usern).exists():
                    return redirect('searchmycar')

                # Check if the user is a Driver
                elif Driver.objects.filter(usern=usern).exists():
                    return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password!")
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "Invalid username!")
            return redirect('login')

    return render(request, "login.html")


def Register(request):
    if request.method == 'GET':
        return render(request, "registration.html")

    if request.method == 'POST':
        if 'usern' in request.POST:  # User registration
            # Extract basic user information
            usern = request.POST['usern']
            fname = request.POST['fname']
            email = request.POST['email']
            password = request.POST['password']
            mobile = request.POST['mobile']
            gender = request.POST['gender']
            address = request.POST['address']
            city = request.POST['city']
            state = request.POST['state']
            # Extract additional user information
            college = request.POST['college']
            degree = request.POST['degree']
            field_of_study = request.POST['field_of_study']
            graduation_year = request.POST['graduation_year']
            languages_user = request.POST.getlist('languages_user')
            current_status = request.POST['current-status']
            company_name = request.POST.get('company-name', None)
            role = request.POST.get('role', None)

            # Join the selected languages into a single string
            languages_str = ','.join(languages_user)

            # Print statements to check extracted data
            print("Username:", usern)
            print("Full Name:", fname)
            print("Email:", email)
            print("Password:", password)  # Note: Passwords should not be printed in production
            print("Mobile:", mobile)
            print("Gender:", gender)
            print("Address:", address)
            print("City:", city)
            print("State:", state)
            print("College:", college)
            print("Degree:", degree)
            print("Field of Study:", field_of_study)
            print("Graduation Year:", graduation_year)
            print("Languages Spoken:", languages_str)
            print("Current Status:", current_status)
            print("Company Name:", company_name)
            print("Role:", role)

            # Validate mobile number
            if len(mobile) != 10 or not mobile.isdigit():
                messages.warning(request, "The phone number provided is not valid!")
                return redirect('register')

            try:
                # Create user object
                user = User.objects.create_user(usern, email, password)
                user.save()
                # Create customer object
                cust = Customer.objects.create(
                    usern=usern,
                    fname=fname,
                    email=email,
                    mobile=mobile,
                    gender=gender,
                    address=address,
                    city=city,
                    state=state,
                    college=college,
                    degree=degree,
                    field_of_study=field_of_study,
                    graduation_year=graduation_year,
                    current_status=current_status,
                    company_name=company_name,
                    role=role,
                    languages=languages_str
                )
                # Save customer object
                cust.save()
                messages.success(request, "Account created successfully!")
                return redirect('login')
            except IntegrityError:
                messages.warning(request, "Account already exists!")
                return redirect('register')

        elif 'usern_driver' in request.POST:  # Driver registration
            usern = request.POST['usern_driver']
            fname = request.POST['fname_driver']
            email = request.POST['email_driver']
            password = request.POST['password_driver']
            mobile = request.POST['mobile_driver']
            address = request.POST['address_driver']
            gender = request.POST['gender_driver']
            state = request.POST['state_driver']
            city = request.POST['city_driver']
            role = request.POST['role']
            year_of_experience = request.POST['year-of-experience']
            languages_driver = request.POST.getlist('languages_driver')
            services = request.POST.getlist('services_driver[]')
            description = request.POST['description_driver']
            cropped_image_data = request.POST.get('cropped_image_data')

            # Join the selected languages into a single string
            languages_str = ','.join(languages_driver)

            print("Username:", usern)
            print("Full Name:", fname)
            print("Email:", email)
            print("Password:", password)  # Note: Passwords should not be printed in production
            print("Mobile:", mobile)
            print("Address:", address)
            print("Gender:", gender)
            print("State:", state)
            print("City:", city)
            print("Role:", role)
            print("Year of Experience:", year_of_experience)
            print("Languages Spoken:", languages_str)
            print("Services:", services)
            print("Description:", description)

            if len(mobile) != 10 or not mobile.isdigit():
                messages.warning(request, "The phone number provided is not valid!")
                return redirect('register')

            try:
                user = User.objects.create_user(username=usern, email=email, password=password)
                user.save()
                driver = Driver.objects.create(
                    usern=usern,
                    fname=fname,
                    email=email,
                    mobile=mobile,
                    address=address,
                    gender=gender,
                    state=state,
                    city=city,
                    role=role,
                    year_of_experience=year_of_experience,
                    languages_spoken=languages_str,
                    services=services,
                    description=description
                )
                cropped_image_data = request.POST['cropped_image_data']
                if cropped_image_data:
                    format, imgstr = cropped_image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'{usern}_profile_picture.{ext}')
                    driver.profile_picture.save(data.name, data)
                    driver.save()
                else:
                    img_data = None
                messages.success(request, "Account created successfully!")
                return redirect('login')
            except IntegrityError:
                messages.warning(request, "Account already exists!")
                return redirect('register')

    return render(request, "registration.html")


from collections import defaultdict

def generate_time_intervals():

    current_time = datetime.strptime("12:00 AM", "%I:%M %p")
    time_strings = []
    for _ in range(96):
        time_strings.append(current_time.strftime("%I:%M %p"))
        current_time += timedelta(minutes=15)
    return time_strings

@login_required
def calendar_view(request):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    times = generate_time_intervals()
    context = {}

    if request.method == 'POST':
        username = request.user.username
        new_entries = []
        has_overlap = False

        for day in days:
            checkbox = request.POST.get(f'{day.lower()}_checkbox', False) == 'on'
            if checkbox:
                from_times = request.POST.getlist(f'{day.lower()}_from_time')
                to_times = request.POST.getlist(f'{day.lower()}_to_time')

                for i in range(len(from_times)):
                    from_time_str = from_times[i]
                    to_time_str = to_times[i]
                    from_time = datetime.strptime(from_time_str, "%I:%M %p")
                    to_time = datetime.strptime(to_time_str, "%I:%M %p")

                    if to_time == from_time:
                        messages.error(request,
                                       f"From time and To time cannot be the same")
                        has_error = True
                        break

                    if to_time <= from_time:
                        to_time += timedelta(days=1)

                    new_entry = {
                        'day': day,
                        'from_time': from_time,
                        'to_time': to_time
                    }

                    # Check for overlap with existing new entries
                    for entry in new_entries:
                        if entry['day'] == day:
                            if (entry['from_time'] < to_time and from_time < entry['to_time']):
                                has_overlap = True
                                messages.error(request,
                                               f"Time overlaps with another slot")
                                break

                    new_entries.append(new_entry)
                    if has_overlap:
                        break

        # Save new entries if no overlap is found
        if not has_overlap:
            CalendarData.objects.filter(username=username, is_deleted=False).update(is_deleted=True)
            print("has_overlap ", new_entries)
            for entry in new_entries:
                try:
                    CalendarData.objects.create(
                        day=entry['day'],
                        checkbox=True,
                        from_time=entry['from_time'].time(),
                        to_time=entry['to_time'].time(),
                        username=username
                    )
                except Exception as e:
                    messages.error(request, f"Error: {e}")

    # Refresh latest schedule data after adding new entries
    context = buildContextForSchedules(load_latest_schedule(request.user.username, days), days, times)
    return render(request, "calendar.html", context)


def buildContextForSchedules(schedule_data, days, times):
    return {
            'schedule_data': schedule_data,
            'days': days,
            'times': times
        }


def load_latest_schedule(username, days):
    latest_schedule_data = []
    try:
        for day in days:
            schedule_entries = list(CalendarData.objects.filter(
                username=username, day=day, is_deleted=False
            ))
            latest_schedule_data.extend(schedule_entries)
        print("latest_schedule_data ", latest_schedule_data)
    except CalendarData.DoesNotExist as e:
        messages.error(request, f"Error: {e}")
    return latest_schedule_data


@login_required
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(CalendarData, id=schedule_id)
    DeletedSchedule.objects.create(
        day=schedule.day,
        from_time=schedule.from_time,
        to_time=schedule.to_time,
        username=schedule.username
    )
    schedule.delete()
    # messages.success(request, 'Schedule deleted successfully')
    return redirect('calendar')


# @login_required
# def delete_schedule(request, schedule_id):
#     schedule = get_object_or_404(CalendarData, id=schedule_id)
#     DeletedSchedule.objects.create(
#         day=schedule.day,
#         from_time=schedule.from_time,
#         to_time=schedule.to_time,
#         username=schedule.username
#     )
#     schedule.delete()
#     # messages.success(request, 'Schedule deleted successfully')
#     return redirect('calendar')

@login_required
def Search(request):
    if request.method == "GET":
        search_term = request.GET.get('search_term', '').strip()
        year_of_experience = request.GET.get('year_of_experience', '').strip()

        mentors = Driver.objects.all()  # Start with all mentors

        if search_term:
            terms = search_term.split()  # Split input into individual terms (roles)
            search_conditions = Q()

            for term in terms:
                # Add conditions to match each term against relevant fields
                term_conditions = (Q(usern__icontains=term) |
                                   Q(role__icontains=term) |
                                   Q(services__icontains=term) |
                                   Q(languages_spoken__icontains=term))
                search_conditions |= term_conditions  # Combine with OR for each term

            # Filter mentors based on combined search conditions
            mentors = mentors.filter(search_conditions)

        if year_of_experience:
            if year_of_experience == "greater_than_2":
                mentors = mentors.filter(year_of_experience__gt=2)
            else:
                mentors = mentors.filter(year_of_experience=year_of_experience)

        # Process mentors to clean up services for template display
        for mentor in mentors:
            if mentor.services:
                # Clean up services: strip square brackets, split by comma, strip quotes
                services = mentor.services.strip("[]").split(",")
                cleaned_services = [service.strip().strip('"\'') for service in services]
                mentor.services = cleaned_services

        # Process each mentor to split languages_spoken
        for mentor in mentors:
            if mentor.languages_spoken:
                mentor.languages_spoken = mentor.languages_spoken.split(',')

        # Collect unique filter items
        unique_roles = set(mentor.role for mentor in mentors if mentor.role)
        unique_years_of_experience = set(mentor.year_of_experience for mentor in mentors if mentor.year_of_experience)
        unique_languages_spoken = set(
            language for mentor in mentors if mentor.languages_spoken for language in mentor.languages_spoken)
        unique_services = set(service for mentor in mentors if mentor.services for service in mentor.services)

        return render(request, 'search.html', {
            'mentors': mentors,
            'search_term': search_term,
            'year_of_experience': year_of_experience,
            'unique_roles': unique_roles,
            'unique_years_of_experience': unique_years_of_experience,
            'unique_languages_spoken': unique_languages_spoken,
            'unique_services': unique_services,
        })

    return render(request, "search.html")


# Function to show logged in user's account details
@login_required(login_url='login')
def page(request, username):
    context = {}
    try:
        cust = Customer.objects.get(usern=username)
        context = {'cust': cust}
    except Customer.DoesNotExist:
        try:
            driver = Driver.objects.get(usern=username)
            context = {
                'user_type': 'driver',
                'name': driver.fname,
                'description': driver.description,
                'profile_picture': driver.profile_picture.url if driver.profile_picture else None,
                'services': Service.objects.all()  # Fetch all services for drivers
            }
        except Driver.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('home')

    return render(request, "page.html", context)


def service_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        duration = request.POST.get('duration')
        amount = request.POST.get('amount')

        service = Service(title=title, duration=duration, amount=amount)
        service.save()

        messages.success(request, 'Service successfully saved!')

        return redirect('service_create')

    services = Service.objects.all()
    return render(request, 'service.html', {'services': services})


# def service_detail(request, service_id):
#     service = get_object_or_404(Service, id=service_id)
#     return render(request, 'service_detail_page.html', {'service': service})
# from django.shortcuts import render, get_object_or_404
# from .models import Service
@login_required(login_url='login')
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    amount_in_paise = int(service.amount * 100)

    # Fetch all calendar data
    calendar_data = CalendarData.objects.all()

    # Create a dictionary to map day names to dates
    current_date = datetime.now()
    day_name_to_date = {}
    for i in range(7):  # Check for the next 7 days
        date_with_day = current_date + timedelta(days=i)
        day_name = date_with_day.strftime("%a")  # Get the abbreviated day name (e.g., "Mon")
        formatted_date = date_with_day.strftime("%d %b")  # e.g., "01 Jul"
        day_name_to_date[day_name] = formatted_date

    # Create formatted calendar data
    formatted_calendar_data = []
    for calendar in calendar_data:
        formatted_date = day_name_to_date.get(calendar.day[:3], "")
        formatted_calendar_data.append({
            'day': calendar.day[:3],
            'from_time': calendar.from_time,
            'to_time': calendar.to_time,
            'formatted_date': formatted_date,
        })

    context = {
        'service': service,
        'amount_in_paise': amount_in_paise,
        'calendar_data': formatted_calendar_data,
    }

    return render(request, 'service_detail_page.html', context)


# Function to help user contact the admin
def Contactus(request):
    if request.method == "GET":
        return render(request, "contact.html")

    if request.method == "POST":
        # m=sql.connect(host="localhost", user="root", passwd="Web@123456", database='carpooling')
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        msg = request.POST['msg']
        if len(phone) != 10 or phone.isdigit() == False:
            messages.warning(request, "The phone number provided is not 10 digits!")
        elif phone.startswith(('1', '2', '3', '4', '5', '0')):
            messages.warning(request, "The phone number provided is not valid!")
        else:
            contact_us = ContactUs.objects.create(name=name, email=email, phone=phone, msg=msg)

            # save the contact details in database
            # print(request.user)
            # customer = Customer.objects.get(usern=user_name)
            #    contact_us = ContactUs.objects.create(name=name, email=email, phone=phone, msg=msg, cust=customer)
            # else:
            #    contact_us = ContactUs.objects.create(name=name, email=email, phone=phone, msg=msg, cust=None)

            # print(contact_us)
            contact_us.save()
            # m.commit()
            messages.success(request, "Thank you for contacting us, we will reach you soon.")

        return render(request, "contact.html")


# Function to show details of the car to the user, but if the user is not logged in then take to login page
@login_required(login_url='login')
def Cardetails(request, car_id):
    if request.method == "GET":
        car = Mycar.objects.get(pk=car_id)
        context = {'car': car}
        return render(request, "cardetails.html", context)

    # Function to book the car
    if request.method == "POST":
        # m=sql.connect(host="localhost", user="root", passwd="Web@123456", database='carpooling')
        # name=request.POST['name']
        contact = request.POST['contact']
        email = request.POST['email']
        pickup = request.POST['pickup']
        dropoff = request.POST['dropoff']
        pick_add = request.POST['pick_add']
        drop_add = request.POST['drop_add']
        if len(contact) != 10 or contact.isdigit() == False:
            messages.warning(request, "The phone number provided is not 10 digits!")
        elif contact.startswith(('1', '2', '3', '4', '5', '0')):
            messages.warning(request, "The phone number provided is not valid!")
        else:
            user = request.user
            print(user)
            cust = Customer.objects.get(usern=user)
            print(cust)
            car = Mycar.objects.get(pk=car_id)
            overlap_bookings = Booking.objects.filter(car=car, pickup=pickup, dropoff=dropoff)
            if overlap_bookings.exists():
                messages.error(request, "The car is not available for the selected dates.")
                return redirect('cardetails', car_id=car_id)

            cars = Booking.objects.create(name=cust, car=car, email=email, contact=contact, pickup=pickup,
                                          dropoff=dropoff, pick_add=pick_add, drop_add=drop_add)
            cars.save()
            # m.commit()
            # messages.success(request, "Your booking has been submitted successfully!")
            return redirect('bookedcar', car_id=car_id)
    return redirect('cardetails', car_id=car_id)


# Function to show the booked cars, booked by the user
def Booked(request, car_id):
    if request.method == "GET":
        if request.user.is_authenticated:
            messages.success(request, "Your booking has been done successfully!")
            user = request.user
            cust = Customer.objects.get(usern=user)

            book = Booking.objects.get(car=car_id, name=cust)
            print(book)
            context = {'book': book}
            return render(request, "booked.html", context)


# Function to show dashboard to the logged in users
def dash(request):
    if request.user.is_authenticated:
        print(request.user)
        return render(request, "dashboard.html")


def bookings_view(request):
    return render(request, 'bookings.html')  # Assuming 'bookings.html' is the HTML page you want to render


def service_view(request):
    # Your logic for rendering the service page goes here
    return render(request, 'service.html')


def testimonial_view(request):
    # Add any logic you need here
    return render(request, 'testimonial.html')


# Function to show logged in user's bookings from the dashboard
def MyBookings(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = request.user
            cust = Customer.objects.get(usern=user)
            custs = Booking.objects.filter(name=cust)
            print(custs)
            context = {'custs': custs}
            return render(request, "mybooking.html", context)
    # if request.method == 'POST':
    #    if request.user.is_authenticated:
    #       user=request.user
    #        cust=Customer.objects.get(usern=user)
    #        custs=Booking.objects.get(name=cust)
    #        print(custs)
    #        context={'custs':custs}
    #        return render(request, "mybooking.html",context)


# Function to show logged in user's account details
def MyAccount(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = request.user
            cust = Customer.objects.get(usern=user)
            # print(cust)
            context = {'cust': cust}
            return render(request, "myaccount.html", context)


# Function to show logged in user's cars booked by other customer's
def CustomerBookings(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = request.user
            cust = Customer.objects.get(usern=user)
            mybook = Booking.objects.filter(name=cust)
            mycar = Mycar.objects.filter(cust=cust)
            otherbookings = Booking.objects.filter(car__in=mycar).exclude(name=cust)
            context = {'otherbookings': otherbookings}
            return render(request, "cust_booking.html", context)


# Function to show logged in user, their added cars
def MyCarList(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = request.user
            username = Customer.objects.get(usern=user)
            custs = Mycar.objects.filter(cust=username)
            print(custs)
            context = {'custs': custs}
            return render(request, "mycar_list.html", context)


# Function to show all the cars to the logged in or unloggedin users on the allcars.html
def Cars(request):
    if request.method == 'GET':
        mycars = Mycar.objects.all()
        context = {'mycars': mycars}
        return render(request, "allcars.html", context)

    # if request.method == 'POST':
    #    if request.user.is_authenticated:
    #        return render("")


# Function to help logged in user to change password on change.html
def Change(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, "change.html")

    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            print(user)
            old_password = request.POST['old_password']
            print(old_password)
            new_password = request.POST['new_password']
            print(new_password)
            confirm_password = request.POST['confirm_password']
            print(confirm_password)
            usern = authenticate(request, username=user, password=old_password)
            print(usern)
            if usern is None:
                messages.error(request, 'The old password is incorrect!')
                return redirect('changepassword')

            if new_password != confirm_password:
                messages.error(request, 'The new password and confirm password does not match!')
                return redirect('changepassword')

            print(user.password)
            user.password = make_password(new_password)
            user.save()
            login(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('changepassword')
    return render(request, 'change.html')


# Function to add user's car in the database
def Addcar(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, "addmycar.html")

    if request.method == 'POST':
        if request.user.is_authenticated:
            # m=sql.connect(host="localhost", user="root", passwd="prachi26", database='carpooling')
            car_num = request.POST['car_num']
            car_name = request.POST['car_name']
            from_place = request.POST['from_place']
            to_place = request.POST['to_place']
            car_type = request.POST['car_type']
            company = request.POST['company']
            price = request.POST['price']
            from_date = request.POST['from_date']
            to_date = request.POST['to_date']
            car_img = request.FILES['car_img']
            custom = Customer.objects.get(usern=request.user)
            print(custom)
            car = Mycar.objects.filter(car_num=car_num)
            if car.exists():
                messages.warning(request, 'Car Already exists')
                return redirect('addmycar')
            obj = Mycar.objects.create(car_num=car_num, from_date=from_date, to_date=to_date, car_name=car_name,
                                       from_place=from_place, to_place=to_place, car_type=car_type, company=company,
                                       price=price, car_img=car_img, cust=custom)
            obj.save()
            # m.commit()
            return redirect('dashboard')

    return render(request, "addmycar.html")


def logout_user(request):
    if request.user.is_authenticated:
        # request.session.clear()
        # print('User is authenticated')
        logout(request)
    return redirect('home')


# Initialize Razorpay client
client = razorpay.Client(auth=('rzp_test_0Mwm4Zy3PDU4AD', 'GOThHWUCVDXGMQsg7Zw0iLi0'))


@csrf_exempt
def payment(request):
    if request.method == 'POST':
        try:
            amount = 50000  # amount in paise
            currency = 'INR'
            payment_capture = '1'

            order = client.order.create({
                'amount': amount,
                'currency': currency,
                'payment_capture': payment_capture,
            })

            return JsonResponse(order)
        except razorpay.errors.BadRequestError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Something went wrong'}, status=500)

    return render(request, "payment.html")


@csrf_exempt
def payment_verification(request):
    if request.method == 'POST':
        try:
            data = request.POST
            params_dict = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }

            client.utility.verify_payment_signature(params_dict)

            return JsonResponse({'status': 'Payment successful'})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'Payment verification failed'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'Something went wrong'}, status=500)

    return HttpResponse(status=405)
