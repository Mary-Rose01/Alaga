from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import SeniorRegistrationForm
from .models import (
    ChronicCondition, EmergencyContact, SeniorAllergy, SeniorAssignment,
    SeniorCitizen, SeniorCondition,
)

User = get_user_model()


def is_mho(user):
    return user.is_authenticated and getattr(user, 'role', '') == 'MHO'


@login_required
def senior_list_view(request):
    """Registry of senior citizens. BHWs only see their active assignments."""
    seniors = SeniorCitizen.objects.filter(archived_at__isnull=True)
    if getattr(request.user, 'role', '') == 'BHW':
        seniors = seniors.filter(
            assignments__worker=request.user, assignments__unassigned_at__isnull=True
        ).distinct()

    q = request.GET.get('q', '').strip()
    if q:
        seniors = seniors.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(osca_id__icontains=q)
        )
    barangay = request.GET.get('barangay', '').strip()
    if barangay:
        seniors = seniors.filter(barangay=barangay)

    barangays = (
        SeniorCitizen.objects.exclude(barangay='')
        .values_list('barangay', flat=True).distinct().order_by('barangay')
    )
    return render(request, 'seniors/senior_list.html', {
        'seniors': seniors.order_by('last_name', 'first_name'),
        'search_query': q,
        'selected_barangay': barangay,
        'barangays': barangays,
    })


@login_required
def senior_register_view(request):
    """Register a senior citizen record (separate from BHW/MHO worker registration)."""
    if request.method == 'POST':
        form = SeniorRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                senior = form.save(commit=False)
                senior.registered_by = request.user
                senior.status = 'Active'
                senior.save()

                cd = form.cleaned_data
                for name in [c.strip() for c in cd['chronic_conditions'].split(',') if c.strip()]:
                    condition, _ = ChronicCondition.objects.get_or_create(name=name[:100])
                    SeniorCondition.objects.get_or_create(senior=senior, condition=condition)
                for allergen in [a.strip() for a in cd['allergies'].split(',') if a.strip()]:
                    SeniorAllergy.objects.create(senior=senior, allergen=allergen[:100])
                if cd['contact_person']:
                    EmergencyContact.objects.create(
                        senior=senior,
                        full_name=cd['contact_person'],
                        relationship=cd['contact_relationship'],
                        phone_number=cd['contact_phone'],
                        is_primary=True,
                    )
                # A BHW who registers a senior becomes their primary worker.
                if getattr(request.user, 'role', '') == 'BHW':
                    SeniorAssignment.objects.create(
                        senior=senior, worker=request.user,
                        assigned_by=request.user, is_primary=True,
                    )
            messages.success(request, f'{senior} was registered successfully.')
            return redirect('senior_list')
        messages.error(request, 'Please correct the highlighted fields.')
    else:
        form = SeniorRegistrationForm(initial={
            'city_municipality': 'Danao City', 'province': 'Cebu',
        })
    return render(request, 'seniors/senior_register.html', {'form': form})


@login_required
@user_passes_test(is_mho)
def bhw_workload_view(request):
    """MHO-only workload overview and assignment form using existing tables."""
    if request.method == 'POST':
        senior_id = request.POST.get('senior_id')
        worker_id = request.POST.get('worker_id')
        try:
            senior = SeniorCitizen.objects.get(pk=senior_id)
            worker = User.objects.get(pk=worker_id, role='BHW', is_active=True)
            with transaction.atomic():
                # Close any current assignment for this senior before reassigning.
                SeniorAssignment.objects.filter(
                    senior=senior, unassigned_at__isnull=True
                ).update(unassigned_at=timezone.now())
                SeniorAssignment.objects.create(
                    senior=senior,
                    worker=worker,
                    assigned_by=request.user,
                    is_primary=True,
                )
            messages.success(request, f'{senior} assigned to {worker.get_full_name() or worker.username}.')
        except (SeniorCitizen.DoesNotExist, User.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'Please select a valid senior citizen and active BHW.')
        return redirect('bhw_workload')

    active_assignments = SeniorAssignment.objects.filter(
        unassigned_at__isnull=True
    ).select_related('senior', 'worker', 'assigned_by').order_by('worker__last_name', 'senior__last_name')

    workers = User.objects.filter(role='BHW', is_active=True).annotate(
        active_senior_count=Count(
            'assigned_seniors',
            filter=Q(assigned_seniors__unassigned_at__isnull=True),
            distinct=True,
        )
    ).order_by('last_name', 'first_name')

    assigned_senior_ids = active_assignments.values_list('senior_id', flat=True)
    unassigned_seniors = SeniorCitizen.objects.exclude(pk__in=assigned_senior_ids).order_by('last_name', 'first_name')

    return render(request, 'seniors/bhw_workload.html', {
        'assignments': active_assignments,
        'workers': workers,
        'unassigned_seniors': unassigned_seniors,
        'total_workers': workers.count(),
        'total_assignments': active_assignments.count(),
        'unassigned_count': unassigned_seniors.count(),
    })
