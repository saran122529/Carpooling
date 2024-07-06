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
from website.models import Customer, ContactUs, Driver, CalendarData, DeletedSchedule, Service, Transaction
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
from datetime import datetime,timedelta
from .models import Service, CalendarData
from django.http import HttpResponse



# Create your views here.
#Home page
def home(request):
    return render(request, "home.html")

#Function to help login the user and open dashboard
def LoginUser(request):
    if request.method == "GET":
        return render(request, "login.html")

    if request.method == "POST":
        usern = request.POST.get('usern')  # Use get() to safely get form input
        password = request.POST.get('password')

        try:
            user = authenticate(username=usern, password=password)
            if user is not None:
                login(request, user)

                # Check if the user is a Customer
                if Customer.objects.filter(usern=user).exists():
                    return redirect('searchmycar')

                # Check if the user is a Driver
                elif Driver.objects.filter(usern=user).exists():
                    return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password!")
        except User.DoesNotExist:
            messages.error(request, "Invalid username!")

    return redirect('login')



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

            
            # Validate mobile number
            if len(mobile) != 10 or not mobile.isdigit():
                messages.warning(request, "The phone number provided is not valid!")
                return redirect('register')

            try:
                # Create user object
                user = User.objects.create_user(username=usern, email=email, password=password)
                user.save()
                # Create customer object
                cust = Customer.objects.create(
                    usern=user,
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


            if len(mobile) != 10 or not mobile.isdigit():
                messages.warning(request, "The phone number provided is not valid!")
                return redirect('register')

            try:
                user = User.objects.create_user(username=usern, email=email, password=password)
                user.save()
                driver = Driver.objects.create(
                    usern=user,
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


@login_required
def calendar_view(request):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if request.method == 'GET':
        latest_schedule_data = {}
        for day in days:
            try:
                schedule_entry = CalendarData.objects.filter(
                    user=request.user, day=day, is_deleted=False
                ).latest('id')
                latest_schedule_data[day] = schedule_entry
            except CalendarData.DoesNotExist:
                pass

        context = {
            'schedule_data': latest_schedule_data.values(),
            'days': days
        }
        return render(request, "calendar.html", context)

    elif request.method == 'POST':
        user = request.user
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

                    if to_time <= from_time:
                        to_time += timedelta(days=1)

                    # Check against existing entries
                    existing_entries = CalendarData.objects.filter(
                        user=user, day=day, is_deleted=False
                    )

                    for existing_entry in existing_entries:
                        existing_from_time = datetime.combine(datetime.today(), existing_entry.from_time)
                        existing_to_time = datetime.combine(datetime.today(), existing_entry.to_time)
                        if existing_to_time <= existing_from_time:
                            existing_to_time += timedelta(days=1)

                        print(
                            f"Comparing new entry from {from_time} to {to_time} with existing entry from {existing_from_time} to {existing_to_time}")

                        if (
                                (existing_from_time <= from_time < existing_to_time) or
                                (existing_from_time < to_time <= existing_to_time) or
                                (from_time <= existing_from_time and to_time > existing_from_time)
                        ):
                            messages.error(request,
                                           f"Time slot from {existing_entry.from_time} to {existing_entry.to_time} on {day} overlaps with another slot.")
                            has_overlap = True
                            break

                    if has_overlap:
                        break

                    # Check against new entries
                    for new_entry in new_entries:
                        new_from_time = new_entry['from_time']
                        new_to_time = new_entry['to_time']

                        if new_to_time <= new_from_time:
                            new_to_time += timedelta(days=1)

                        print(
                            f"Comparing new entry from {from_time} to {to_time} with another new entry from {new_from_time} to {new_to_time}")

                        if (
                                (new_from_time <= from_time < new_to_time) or
                                (new_from_time < to_time <= new_to_time) or
                                (from_time <= new_from_time and to_time > new_from_time)
                        ):
                            messages.error(request, f"Time overlaps with another slot on {day}")
                            has_overlap = True
                            break

                    if has_overlap:
                        break

                    new_entries.append({
                        'day': day,
                        'from_time': from_time,
                        'to_time': to_time
                    })

                if has_overlap:
                    break

        if not has_overlap:
            CalendarData.objects.filter(user=user, is_deleted=False).update(is_deleted=True)

            for entry in new_entries:
                try:
                    CalendarData.objects.create(
                        day=entry['day'],
                        checkbox=True,
                        from_time=entry['from_time'].time(),
                        to_time=entry['to_time'].time(),
                        user=user,
                        username=username
                    )
                except Exception as e:
                    messages.error(request, f"Error: {e}")

        return redirect('calendar')    
    
@login_required
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(CalendarData, id=schedule_id)
    DeletedSchedule.objects.create(
        day=schedule.day,
        from_time=schedule.from_time,
        to_time=schedule.to_time,
        user_id=schedule.user.id,  # Store user ID
        username=schedule.user.username  # Store username
    )
    schedule.delete()
    # messages.success(request, 'Schedule deleted successfully')
    return redirect('calendar')


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
        unique_languages_spoken = set(language for mentor in mentors if mentor.languages_spoken for language in mentor.languages_spoken)
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
    try:
        # Attempt to fetch Customer by username
        cust = Customer.objects.get(usern__username=username)
        context = {'cust': cust}
        return render(request, "page.html", context)
    except Customer.DoesNotExist:
        try:
            # Attempt to fetch Driver by username
            driver = Driver.objects.get(usern__username=username)
            context = {
                'user_type': 'driver',
                'name': driver.fname,
                'description': driver.description,
                'profile_picture': driver.profile_picture.url if driver.profile_picture else None,
                'services': Service.objects.filter(user=driver.usern)  # Fetch all services for drivers
            }
            return render(request, "page.html", context)
        except Driver.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('home')

@login_required
def service_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        duration = request.POST.get('duration')
        amount = request.POST.get('amount')

        service = Service(title=title, duration=duration, amount=amount, user=request.user)
        service.save()

        messages.success(request, 'Service successfully saved!')

        return redirect('service_create')

    services = Service.objects.filter(user=request.user)  # Filter services by the logged-in user
    

    return render(request, 'service.html', {'services': services})

@login_required
def service_delete(request, service_id):
    service = get_object_or_404(Service, id=service_id, user=request.user)  # Ensure the service belongs to the user
    if request.method == 'DELETE':
        service.delete()
        messages.success(request, 'Service deleted successfully')
        return JsonResponse({'message': 'Service deleted successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required(login_url='login')
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    amount_in_paise = int(service.amount * 100)
    
     # Fetch the driver based on service user (assuming user in Service model)
    driver = Driver.objects.get(usern=service.user)
    
    # Fetch calendar data based on driver's usern
    calendar_data = CalendarData.objects.filter(username=driver.usern.username)
    
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
        'user': request.user,  # Pass the logged-in user object to the template
        'driver_username': driver.usern.username,  # Add driver's username to context
    }

    return render(request, 'service_detail_page.html', context)



#Function to help user contact the admin
def Contactus(request):
    if request.method=="GET":
        return render(request, "contact.html")
    
    if request.method=="POST":
        # m=sql.connect(host="localhost", user="root", passwd="Web@123456", database='carpooling')
        name=request.POST['name']
        email=request.POST['email']
        phone=request.POST['phone']
        msg=request.POST['msg']
        if len(phone)!=10 or phone.isdigit()==False:
            messages.warning(request, "The phone number provided is not 10 digits!")
        elif phone.startswith(('1', '2', '3', '4', '5', '0')):
            messages.warning(request, "The phone number provided is not valid!")
        else:
            contact_us = ContactUs.objects.create(name=name, email=email, phone=phone, msg=msg)

        
        # save the contact details in database
            #print(request.user)
            #customer = Customer.objects.get(usern=user_name)
            #    contact_us = ContactUs.objects.create(name=name, email=email, phone=phone, msg=msg, cust=customer)
            #else:
            #    contact_us = ContactUs.objects.create(name=name, email=email, phone=phone, msg=msg, cust=None)

            #print(contact_us)
            contact_us.save()
            # m.commit()
            messages.success(request, "Thank you for contacting us, we will reach you soon.")

        return render(request, "contact.html")


# Function to show dashboard to the logged in users
def dash(request):
     if request.user.is_authenticated:
         print(request.user)
         return render(request, "dashboard.html")

@login_required
def bookings_view(request):
    # Filter transactions based on the logged-in driver's username
    transactions = Transaction.objects.filter(driver_username=request.user.username)

    context = {
        'transactions': transactions
    }
    return render(request, 'bookings.html', context)

def service_view(request):
    # Your logic for rendering the service page goes here
    
    services = Service.objects.filter(user=request.user)  # Filter services by the logged-in user
    context = {'services': services}

    return render(request, 'service.html', context)



def testimonial_view(request):
    # Add any logic you need here
    return render(request, 'testimonial.html')


#Function to show logged in user's bookings from the dashboard
# 
@login_required
def MyBookings(request):
    # Filter transactions based on the logged-in user's username
    transactions = Transaction.objects.filter(username=request.user.username)

    context = {
        'transactions': transactions
    }
    return render(request, "mybooking.html", context)
    


#Function to show logged in user's account details
def MyAccount(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = request.user
            cust=Customer.objects.get(usern=user)
            #print(cust)
            context={'cust': cust}
            return render(request, "myaccount.html", context)





#Function to help logged in user to change password on change.html
def Change(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, "change.html")
    
    if request.method=='POST':
        if request.user.is_authenticated:
            user=request.user
            print(user)
            old_password=request.POST['old_password']
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
            
            

def logout_user(request):
    if request.user.is_authenticated:
        #request.session.clear()
        #print('User is authenticated')
        logout(request)
    return redirect('home')

# Initialize Razorpay client
client = razorpay.Client(auth=('rzp_test_0Mwm4Zy3PDU4AD', 'GOThHWUCVDXGMQsg7Zw0iLi0'))

@csrf_exempt
def payment(request, pk=None):
    try:
        if request.method == 'POST':
            data = request.POST
            service_title = data['service_title']
            service_duration = data['service_duration']
            service_amount = data['service_amount']
            selected_day = data['selected_day']
            selected_time = data['selected_time']
            username = data['username']  # Fetch the username from the POST data
            driver_username = data['driver_username']  # Get driver's username from POST data
        else:
            service = get_object_or_404(Service, pk=pk)
            service_title = service.title
            service_duration = service.duration
            service_amount = service.amount
            selected_day = ''
            selected_time = ''
            username = ''
            driver_username = ''

        amount = int(float(service_amount) * 100)  # amount in paise
        currency = 'INR'
        payment_capture = '1'

        order = client.order.create({
            'amount': amount,
            'currency': currency,
            'payment_capture': payment_capture,
        })

        if request.method == 'POST':
            # Save the transaction info with a pending payment status
            Transaction.objects.create(
                service_title=service_title,
                service_duration=service_duration,
                service_amount=service_amount,
                selected_day=selected_day,
                selected_time=selected_time,
                payment_status='Pending',
                razorpay_order_id=order['id'],
                username=username,
                driver_username=driver_username
            )

        context = {
            'order_id': order['id'],
            'amount': amount / 100,  # Convert paise to rupees
            'currency': currency,
        }
        return render(request, 'payment_success.html', context)
    except razorpay.errors.BadRequestError as e:
        context = {'error': str(e)}
        return render(request, 'payment_failure.html', context)
    except Exception as e:
        context = {'error': 'Something went wrong'}
        return render(request, 'payment_failure.html', context)

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

            print(f"Payment Verification Data: {params_dict}")

            # Verify the payment signature
            client.utility.verify_payment_signature(params_dict)

            # Update transaction status to success
            transaction = Transaction.objects.get(razorpay_order_id=data['razorpay_order_id'])
            transaction.razorpay_payment_id = data['razorpay_payment_id']
            transaction.razorpay_signature = data['razorpay_signature']
            transaction.payment_status = 'Success'
            transaction.save()

            print(f"Payment Success for Order ID: {data['razorpay_order_id']}")

            return JsonResponse({'status': 'Payment successful'})
        except razorpay.errors.SignatureVerificationError:
            print(f"Signature Verification Failed for Order ID: {data['razorpay_order_id']}")
            transaction = Transaction.objects.get(razorpay_order_id=data['razorpay_order_id'])
            transaction.payment_status = 'Failed'
            transaction.save()
            return JsonResponse({'status': 'Payment verification failed'}, status=400)
        except Exception as e:
            print(f"Exception: {str(e)}")
            return JsonResponse({'status': 'Something went wrong'}, status=500)

    return HttpResponse(status=405)