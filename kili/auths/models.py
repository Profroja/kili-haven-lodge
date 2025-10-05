from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('lodge_attendant', 'Lodge Attendant'),
    ]
    
    mobile_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )],
        help_text="Enter your mobile number with country code"
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='lodge_attendant',
        help_text="Select your role in the system"
    )
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"