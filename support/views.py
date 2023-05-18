from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from tickets.models import Ticket, TicketStatus


@login_required(login_url='/accounts/login/')
def support(request):
    if request.user.is_authenticated and request.user.google_auth or request.user.is_superuser:
        status_closed = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Closed').count()
        status_overdue = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Overdue').count()
        status_ongoin = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Ongoing').count()

        context = {
        'status_closed': status_closed,
        'status_overdue': status_overdue,
        'status_ongoin': status_ongoin,
        }
        return render(request, "support/support.html", context)
    else: return redirect('authentication:main')
