from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('BHW', 'Barangay Health Worker'),
        ('MHO', 'Municipal Health Office Admin'),
    )
    role = models.CharField(max_length=3, choices=ROLE_CHOICES, default='BHW')
    contact_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_role_display()}"