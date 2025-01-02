from django.db import models
from django.contrib.auth.models import User
from dashboard.models import Zone, Product

# Create your models here.


class Profile(models.Model):
    customer = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    image = models.ImageField(default='default.png', upload_to='profile_images')    
    nid = models.CharField(max_length=20, unique=True, blank=True, null= True)  
    title= models.CharField(max_length=40, blank=True, null= True)  
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null= True)    
    joining_date = models.DateField(blank=True, null= True)  

    HEAD_OFFICE = 'HEAD_OFFICE'
    FACTORY = 'FACTORY'
    OTHERS='OTHERS'
    JOB_LOCATION_CHOICES = [
        (HEAD_OFFICE, 'Head Office'),
        (FACTORY, 'Factory'),
        (OTHERS, 'others'),
    ]
    job_location = models.CharField(max_length=20, choices=JOB_LOCATION_CHOICES, blank=True, null= True)     
    zones = models.ManyToManyField(Zone, blank=True, verbose_name="Dealer Zones")   
    products = models.ManyToManyField(Product, blank=True, verbose_name="Dealer Products")

    def __str__(self):
        return f'{self.customer.username}-Profile'
    
    @property
    def last_login(self):
        return self.customer.last_login
 