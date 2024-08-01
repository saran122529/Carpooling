from django.db import models
from django.contrib.auth.models import User
from PIL import Image
# Create your models here.


class Customer(models.Model):
    usern = models.CharField(max_length=80, unique=True, blank=True)
    fname = models.CharField(max_length=80, blank=True)
    email = models.EmailField(max_length=80, unique=True)
    password = models.CharField(max_length=200, default='default_password')
    gender = models.CharField(max_length=20)
    mobile = models.CharField(max_length=11, null=False)
    address = models.CharField(max_length=100, null=False)
    city = models.CharField(max_length=100, null=False)
    state = models.CharField(max_length=100, null=False)
    college = models.CharField(max_length=200, null=True, blank=True)
    degree = models.CharField(max_length=200, null=True, blank=True)
    field_of_study = models.CharField(max_length=200, null=True, blank=True)
    graduation_year = models.CharField(max_length=4, null=True, blank=True)
    current_status = models.CharField(max_length=100, null=True, blank=True)
    company_name = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=200, null=True, blank=True)
    languages = models.CharField(max_length=500, null=True, blank=True)
    

    def __str__(self):
        return str(self.fname)
    
    
class Driver(models.Model):
    usern=models.CharField(max_length=80, unique=True, blank=True)
    fname = models.CharField(max_length=80, blank=True)
    email = models.EmailField(max_length=80, unique=True)
    password = models.CharField(max_length=200, default='default_password')
    mobile = models.CharField(max_length=11, null=False)
    address = models.CharField(max_length=100, null=False)
    gender = models.CharField(max_length=20, default='Unknown')  
    city = models.CharField(max_length=100, null=False, default='')  # Specify a default value
    state = models.CharField(max_length=100, null=False, default='')
    role = models.CharField(max_length=200, null=True, blank=True)
    year_of_experience = models.CharField(max_length=50, null=True, blank=True)
    languages_spoken = models.CharField(max_length=500, null=True, blank=True)
    services = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return str(self.fname)


    
    

class Mycar(models.Model):
    cust=models.ForeignKey(Customer, max_length=100, blank=True, null=True, on_delete=models.SET_NULL)
    car_num=models.CharField(max_length=10, unique=True)
    company=models.CharField(max_length=30)
    car_name=models.CharField(max_length=30)
    car_type=models.CharField(max_length=30)
    from_place=models.CharField(max_length=30)
    to_place=models.CharField(max_length=30)
    from_date=models.DateField(null=True)
    to_date=models.DateField(null=True)
    price=models.FloatField()
    car_img = models.ImageField(upload_to="cars",default="", null = True,blank = True)

    def __str__(self):
        return self.car_num
    
    @property
    def imageURL(self):
        try:
            url = self.car_img.url
        except:
            url = ''
        return url


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.car_img.path)
        if img.height > 1500 or img.width > 1500:
            output_size = (1500, 1500)
            img.thumbnail(output_size)
            img.save(self.car_img.path)

class ContactUs(models.Model):
    name=models.CharField(max_length=80)
    email=models.EmailField(max_length=80, unique=True, blank=False)
    phone=models.CharField(max_length=11, null=False, blank=True)
    msg=models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Booking(models.Model):
    name=models.ForeignKey(Customer,on_delete=models.SET_NULL, null=True)
    car=models.ForeignKey(Mycar,on_delete=models.SET_NULL, null=True)
    contact=models.CharField(max_length=11,null=False)
    email=models.EmailField(max_length=80)
    pickup=models.DateField()
    dropoff=models.DateField()
    pick_add=models.CharField(max_length=100, null=False)
    drop_add=models.CharField(max_length=100, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class CalendarData(models.Model):
    day = models.CharField(max_length=20)
    checkbox = models.BooleanField(default=False)
    from_time = models.TimeField(null=True, blank=True)
    to_time = models.TimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    username = models.CharField(max_length=150, default='')

    @property
    def from_time_formatted(self):
        return self.from_time.strftime('%I:%M %p') if self.from_time else ''

    @property
    def to_time_formatted(self):
        return self.to_time.strftime('%I:%M %p') if self.to_time else ''

    def __str__(self):
        return f"{self.username} - {self.day} - {self.from_time_formatted} to {self.to_time_formatted}"

class DeletedSchedule(models.Model):
    day = models.CharField(max_length=20)
    from_time = models.TimeField()
    to_time = models.TimeField()
    username = models.CharField(max_length=150, default='default_username')  # Add a default value
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.day} - {self.from_time} to {self.to_time} (Deleted at: {self.deleted_at})"

class Service(models.Model):
    title = models.CharField(max_length=100)
    duration = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title