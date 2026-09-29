from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Extended user model (CUSTOMUSER in ERD).
    Inherits: id (PK/bigint), username (UK/varchar150), email (varchar254),
    password (varchar150), first_name (varchar150), last_name (varchar150),
    is_active (boolean), is_staff (boolean), is_superuser (boolean),
    last_login (timestamp), date_joined (timestamp).
    Added: contact_number, role.
    """
    ROLE_CHOICES = (
        ('BHW', 'Barangay Health Worker'),
        ('MHO', 'Municipal Health Office Admin'),
    )
    # ERD: role varchar(25)
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='BHW')
    # ERD: contact_number varchar(15)
    contact_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_role_display()}"


class AuditLog(models.Model):
    """
    AUDITLOG entity in ERD.
    Stores a snapshot of user data at the time of an audited action.
    PK: audit_id (bigint), UK: username.
    All other fields mirror CustomUser fields.
    """
    # ERD: PK audit_id bigint
    # Django auto-generates 'id' as BigAutoField; we use Meta to name the table.
    # UK: username varchar(150)
    username = models.CharField(max_length=150, unique=True)
    # varchar(254)
    email = models.CharField(max_length=254, blank=True)
    # varchar(150)
    password = models.CharField(max_length=150, blank=True)
    # varchar(150)
    first_name = models.CharField(max_length=150, blank=True)
    # varchar(150)
    last_name = models.CharField(max_length=150, blank=True)
    # varchar(15)
    contact_number = models.CharField(max_length=15, blank=True)
    # varchar(25)
    role = models.CharField(max_length=25, blank=True)
    # boolean
    is_active = models.BooleanField(default=True)
    # boolean
    is_staff = models.BooleanField(default=False)
    # boolean
    is_superuser = models.BooleanField(default=False)
    # timestamp
    last_login = models.DateTimeField(null=True, blank=True)
    # timestamp
    date_joined = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'accounts_auditlog'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        return f"AuditLog [{self.pk}] – {self.username}"