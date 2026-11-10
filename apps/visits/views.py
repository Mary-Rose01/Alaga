from datetime import date
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from apps.seniors.models import SeniorAssignment
from .models import HealthVisit


@login_required
def health_alerts_view(request):
    """Display existing visit alerts and follow-up dates; does not create data."""
    visits = HealthVisit.objects.select_related('senior', 'worker').filter(
        Q(alert_level__isnull=False) & ~Q(alert_level__exact='')
        | Q(follow_up_date__isnull=False)
    )

    # BHWs only see alerts for seniors currently assigned to them.
    if getattr(request.user, 'role', '') == 'BHW':
        assigned_ids = SeniorAssignment.objects.filter(
            worker=request.user, unassigned_at__isnull=True
        ).values_list('senior_id', flat=True)
        visits = visits.filter(senior_id__in=assigned_ids)

    level = request.GET.get('level', '').strip()
    search = request.GET.get('q', '').strip()
    if level:
        visits = visits.filter(alert_level__iexact=level)
    if search:
        visits = visits.filter(
            Q(senior__first_name__icontains=search)
            | Q(senior__last_name__icontains=search)
            | Q(alert_reasons__icontains=search)
        )

    today = date.today()
    alerts = list(visits.order_by('-visited_at'))
    for item in alerts:
        item.follow_up_overdue = bool(item.follow_up_date and item.follow_up_date < today)

    context = {
        'alerts': alerts,
        'selected_level': level,
        'search_query': search,
        'critical_count': visits.filter(alert_level__iexact='Critical').count(),
        'warning_count': visits.filter(alert_level__iexact='Warning').count(),
        'overdue_count': visits.filter(follow_up_date__lt=today).count(),
    }
    return render(request, 'visits/health_alerts.html', context)
