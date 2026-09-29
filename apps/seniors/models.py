from django.conf import settings
from django.db import models


class ChronicCondition(models.Model):
    """
    CHRONIC CONDITION entity in ERD.
    Reference/lookup table for chronic medical conditions.
    PK: id (bigint), UK: name (varchar100).
    """
    # PK: id bigint — Django BigAutoField added via DEFAULT_AUTO_FIELD
    # UK: name varchar(100)
    name = models.CharField(max_length=100, unique=True)
    # description text
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'seniors_chroniccondition'
        verbose_name = 'Chronic Condition'
        verbose_name_plural = 'Chronic Conditions'
        ordering = ['name']

    def __str__(self):
        return self.name


class SeniorCitizen(models.Model):
    """
    SENIOR CITIZEN entity in ERD.
    Core entity representing a registered senior citizen.
    PK: id (bigint), FK: registered_by_id → CustomUser.
    UK: osca_id, philhealth_number.
    """
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    CIVIL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Divorced', 'Divorced'),
        ('Separated', 'Separated'),
    ]
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    LIVING_ARRANGEMENT_CHOICES = [
        ('Alone', 'Alone'),
        ('WithFamily', 'With Family'),
        ('WithCaregiver', 'With Caregiver'),
        ('Institution', 'Institution'),
    ]

    # FK: registered_by_id bigint → CustomUser (worker who registered the senior)
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_seniors',
        db_column='registered_by_id',
    )
    # varchar(100)
    first_name = models.CharField(max_length=100)
    # varchar(100)
    middle_name = models.CharField(max_length=100, blank=True)
    # varchar(100)
    last_name = models.CharField(max_length=100)
    # varchar(10)
    suffix = models.CharField(max_length=10, blank=True)
    # date
    birth_date = models.DateField()
    # varchar(1) — 'M' or 'F'
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    # varchar(10)
    civil_status = models.CharField(max_length=10, choices=CIVIL_STATUS_CHOICES, blank=True)
    # varchar(3)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True)
    # varchar(15) — ERD says varchar(12) but 'WithCaregiver' is 13 chars; using 15
    living_arrangement = models.CharField(max_length=15, choices=LIVING_ARRANGEMENT_CHOICES, blank=True)
    # varchar(15)
    contact_number = models.CharField(max_length=15, blank=True)
    # UK: osca_id varchar(30)
    osca_id = models.CharField(max_length=30, unique=True, null=True, blank=True)
    # UK: philhealth_number varchar(30)
    philhealth_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    # varchar(100)
    street_address = models.CharField(max_length=100, blank=True)
    # varchar(100)
    barangay = models.CharField(max_length=100, blank=True)
    # varchar(100)
    city_municipality = models.CharField(max_length=100, blank=True)
    # varchar(100)
    province = models.CharField(max_length=100, blank=True)
    # decimal (latitude)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # decimal (longitude)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # varchar(100)
    status = models.CharField(max_length=100, blank=True)
    # date
    status_changed_on = models.DateField(null=True, blank=True)
    # date
    date_of_death = models.DateField(null=True, blank=True)
    # varchar(100)
    transferred_to = models.CharField(max_length=100, blank=True)
    # timestamp
    archived_at = models.DateTimeField(null=True, blank=True)
    # timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    # timestamp
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'seniors_seniorcitizen'
        verbose_name = 'Senior Citizen'
        verbose_name_plural = 'Senior Citizens'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name} {self.middle_name}".strip()


class SeniorCondition(models.Model):
    """
    SENIOR CONDITION entity in ERD.
    Junction table: SeniorCitizen ↔ ChronicCondition (diagnosed with).
    PK: id (bigint), FK: senior_id, FK: condition_id.
    """
    # FK: senior_id bigint
    senior = models.ForeignKey(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='conditions',
        db_column='senior_id',
    )
    # FK: condition_id bigint (note: ERD shows 'biint' — typo for bigint)
    condition = models.ForeignKey(
        ChronicCondition,
        on_delete=models.CASCADE,
        related_name='senior_conditions',
        db_column='condition_id',
    )
    # date
    diagnosed_on = models.DateField(null=True, blank=True)
    # varchar(255)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'seniors_seniorcondition'
        verbose_name = 'Senior Condition'
        verbose_name_plural = 'Senior Conditions'
        unique_together = [('senior', 'condition')]

    def __str__(self):
        return f"{self.senior} – {self.condition}"


class SeniorAssignment(models.Model):
    """
    SENIOR ASSIGNMENT entity in ERD.
    Links a senior to a worker (BHW), tracking who assigned them and whether
    this is the primary assignment.
    PK: id (bigint), FK: senior_id, FK: worker_id, FK: assigned_by_id.
    """
    # FK: senior_id bigint
    senior = models.ForeignKey(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='assignments',
        db_column='senior_id',
    )
    # FK: worker_id bigint → CustomUser (the assigned BHW worker)
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_seniors',
        db_column='worker_id',
    )
    # FK: assigned_by_id bigint → CustomUser (the MHO admin who did the assignment)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='made_assignments',
        db_column='assigned_by_id',
    )
    # boolean
    is_primary = models.BooleanField(default=False)
    # timestamp
    assigned_at = models.DateTimeField(auto_now_add=True)
    # timestamp (nullable — null means still assigned)
    unassigned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'seniors_seniorassignment'
        verbose_name = 'Senior Assignment'
        verbose_name_plural = 'Senior Assignments'

    def __str__(self):
        return f"{self.senior} → {self.worker}"


class EmergencyContact(models.Model):
    """
    EMERGENCY CONTACT entity in ERD.
    Stores emergency contact information for a senior citizen.
    PK: id (bigint), FK: senior_id.
    """
    # FK: senior_id bigint
    senior = models.ForeignKey(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
        db_column='senior_id',
    )
    # varchar(200)
    full_name = models.CharField(max_length=200)
    # varchar(100)
    relationship = models.CharField(max_length=100, blank=True)
    # varchar(100)
    phone_number = models.CharField(max_length=100, blank=True)
    # boolean
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'seniors_emergencycontact'
        verbose_name = 'Emergency Contact'
        verbose_name_plural = 'Emergency Contacts'

    def __str__(self):
        return f"{self.full_name} ({self.relationship}) for {self.senior}"


class SeniorAllergy(models.Model):
    """
    SENIOR ALLERGY entity in ERD.
    Records known allergies for a senior citizen.
    PK: id (bigint), FK: senior_id.
    """
    # FK: senior_id bigint
    senior = models.ForeignKey(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='allergies',
        db_column='senior_id',
    )
    # varchar(100)
    allergen = models.CharField(max_length=100)
    # varchar(100)
    reaction = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'seniors_seniorallergy'
        verbose_name = 'Senior Allergy'
        verbose_name_plural = 'Senior Allergies'

    def __str__(self):
        return f"{self.senior} – {self.allergen}"


class SeniorMedication(models.Model):
    """
    SENIOR MEDICATION entity in ERD.
    Records current and past medications for a senior citizen.
    PK: id (bigint), FK: senior_id.
    """
    # FK: senior_id bigint
    senior = models.ForeignKey(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='medications',
        db_column='senior_id',
    )
    # varchar(100)
    name = models.CharField(max_length=100)
    # varchar(100)
    dosage = models.CharField(max_length=100, blank=True)
    # varchar(100)
    frequency = models.CharField(max_length=100, blank=True)
    # date
    started_on = models.DateField(null=True, blank=True)
    # date (null = ongoing medication)
    ended_on = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'seniors_seniormedication'
        verbose_name = 'Senior Medication'
        verbose_name_plural = 'Senior Medications'

    def __str__(self):
        return f"{self.senior} – {self.name} ({self.dosage})"
