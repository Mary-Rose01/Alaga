from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils import timezone
from .models import SeniorAssignment, SeniorCitizen

User = get_user_model()


def is_mho(user):
    return user.is_authenticated and getattr(user, 'role', '') == 'MHO'


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
