# pyrefly: ignore [missing-import]
from django.conf import settings
# pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from apps.seniors.models import SeniorCitizen


class HealthVisit(models.Model):
    """
    HEALTH VISIT entity in ERD.
    Records each health visit conducted by a worker for a senior citizen.
    PK: id (bigint), FK: senior_id, FK: worker_id.
    """
    VISIT_TYPE_CHOICES = [
        ('Routine', 'Routine'),
        ('Follow-up', 'Follow-up'),
        ('Emergency', 'Emergency'),
    ]
    VISIT_LOCATION_CHOICES = [
        ('Home', 'Home'),
        ('Clinic', 'Clinic'),
        ('Hospital', 'Hospital'),
    ]
    MOBILITY_CHOICES = [
        ('Normal', 'Normal'),
        ('Assisted', 'Assisted'),
        ('Bedbound', 'Bedbound'),
    ]

    # FK: senior_id bigint → SeniorCitizen
    senior = models.ForeignKey(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='health_visits',
        db_column='senior_id',
    )
    # FK: worker_id bigint → CustomUser (the BHW who conducted the visit)
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conducted_visits',
        db_column='worker_id',
    )
    # timestamp — when the visit occurred
    visited_at = models.DateTimeField()
    # varchar(10)
    visit_type = models.CharField(max_length=10, choices=VISIT_TYPE_CHOICES, blank=True)
    # varchar(10)
    visit_location = models.CharField(max_length=10, choices=VISIT_LOCATION_CHOICES, blank=True)

    # ── Vital Signs ─────────────────────────────────────────────────────────
    # int
    systolic_bp = models.IntegerField(null=True, blank=True)
    # int
    diastolic_bp = models.IntegerField(null=True, blank=True)
    # decimal
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # decimal
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # int
    pulse_rate = models.IntegerField(null=True, blank=True)
    # int
    respiratory_rate = models.IntegerField(null=True, blank=True)
    # decimal
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    # int
    oxygen_saturation = models.IntegerField(null=True, blank=True)
    # int
    blood_glucose_mgdl = models.IntegerField(null=True, blank=True)
    # int (e.g. 1=fasting, 2=random)
    glucose_type = models.IntegerField(null=True, blank=True)

    # ── Assessment ──────────────────────────────────────────────────────────
    # int (0–10 pain scale)
    pain_score = models.IntegerField(null=True, blank=True)
    # varchar(10)
    mobility = models.CharField(max_length=10, choices=MOBILITY_CHOICES, blank=True)
    # int (boolean-like flag: 0 or 1)
    fell_recently = models.IntegerField(null=True, blank=True)
    # text
    symptoms = models.TextField(blank=True)
    # text
    notes = models.TextField(blank=True)

    # ── Follow-up / Referral ─────────────────────────────────────────────────
    # varchar(50)
    referred_to = models.CharField(max_length=50, blank=True)
    # date
    follow_up_date = models.DateField(null=True, blank=True)
    # varchar(50)
    alert_level = models.CharField(max_length=50, blank=True)
    # text
    alert_reasons = models.TextField(blank=True)

    # ── Timestamps ───────────────────────────────────────────────────────────
    # timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    # timestamp
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'visits_healthvisit'
        verbose_name = 'Health Visit'
        verbose_name_plural = 'Health Visits'
        ordering = ['-visited_at']

    def __str__(self):
        return f"Visit [{self.pk}] – {self.senior} on {self.visited_at:%Y-%m-%d}"
