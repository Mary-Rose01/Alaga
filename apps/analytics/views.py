from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from apps.accounts.models import CustomUser
from apps.seniors.models import SeniorAssignment, SeniorCitizen, SeniorCondition
from apps.visits.models import HealthVisit


@login_required
def reports_view(request):
    """Read-only reports computed from the current ALAGA database."""
    seniors = SeniorCitizen.objects.all()
    visits = HealthVisit.objects.select_related('senior', 'worker')

    # BHW report scope is limited to seniors currently assigned to that worker.
    if getattr(request.user, 'role', '') == 'BHW':
        assigned_ids = SeniorAssignment.objects.filter(
            worker=request.user, unassigned_at__isnull=True
        ).values_list('senior_id', flat=True)
        seniors = seniors.filter(pk__in=assigned_ids)
        visits = visits.filter(senior_id__in=assigned_ids)

    today = date.today()
    age_counts = {'60–69': 0, '70–79': 0, '80–89': 0, '90+': 0}
    for birth_date in seniors.values_list('birth_date', flat=True):
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age >= 90:
            age_counts['90+'] += 1
        elif age >= 80:
            age_counts['80–89'] += 1
        elif age >= 70:
            age_counts['70–79'] += 1
        elif age >= 60:
            age_counts['60–69'] += 1

    barangay_data = list(
        seniors.values('barangay').annotate(total=Count('id')).order_by('-total')[:8]
    )
    for row in barangay_data:
        row['barangay'] = row['barangay'] or 'Not specified'

    condition_data = list(
        SeniorCondition.objects.filter(senior__in=seniors)
        .values('condition__name').annotate(total=Count('senior_id', distinct=True))
        .order_by('-total')[:8]
    )

    monthly_visits = list(
        visits.filter(visited_at__date__gte=today - timedelta(days=180))
        .annotate(month=TruncMonth('visited_at'))
        .values('month').annotate(total=Count('id')).order_by('month')
    )

    total_seniors = seniors.count()
    total_visits = visits.count()
    context = {
        'total_seniors': total_seniors,
        'total_visits': total_visits,
        'male_count': seniors.filter(sex='M').count(),
        'female_count': seniors.filter(sex='F').count(),
        'age_counts': age_counts,
        'barangay_data': barangay_data,
        'condition_data': condition_data,
        'monthly_visits': monthly_visits,
        'recent_visits': visits.order_by('-visited_at')[:10],
    }
    return render(request, 'analytics/reports.html', context)
