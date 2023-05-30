from django.http import JsonResponse
from invoices.models import Invoice
from services.models import Service
from tickets.models import Ticket, TicketComments
from django.db.models import Q
from search.views import search_for_invoice, search_for_service, search_for_ticket


def general_search(request):
    if request.headers.get('x-requested-with'):
        input_value = request.POST.get('input_value')
        result = None
        data = []

        invoice_result = search_for_invoice(request)
        if invoice_result:
            data.extend(invoice_result) if not isinstance(invoice_result, str) else data.append(invoice_result)

        service_result = search_for_service(request)
        if service_result:
            data.extend(service_result) if not isinstance(service_result, str) else data.append(service_result)

        ticket_result = search_for_ticket(request)
        if ticket_result:
            data.extend(ticket_result) if not isinstance(ticket_result, str) else data.append(ticket_result)

        result = data

        if result == ['No invoices...', 'No services...', 'No tickets...']:
            result = 'No results...'
        
        return JsonResponse({'data': result})

    return JsonResponse({})


