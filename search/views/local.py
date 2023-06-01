from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from invoices.models import Invoice
from services.models import Service
from tickets.models import Ticket, TicketComments


# search for invoices

def search_for_invoice(request):
    if request.headers.get('x-requested-with'):
        input_value = request.POST.get('input_value')
        if len(input_value) < 2:
            result = ''
        else:
            if len(input_value) % 2 != 0:
                input_value = input_value[:-1]
            result = None
            queryset = Invoice.objects.filter(Q(invoice_id__icontains=input_value) |
                                            Q(created_at__icontains=input_value) |
                                            Q(price__icontains=input_value) |
                                            Q(status__value__icontains=input_value)).distinct()

            if all([len(queryset) > 0, len(input_value) > 0]):
                data = []
                for element in queryset:
                    item = {'Invoice': {'pk': element.pk,
                                        'number': element.invoice_id,
                                        'price': element.price,
                                        'status': element.status.value,
                                        }}
                    data.append(item)
                result = data
            else:
                result = 'No invoices...'
            
        return result
    

def invoice_search(request):
    result = search_for_invoice(request)
    
    return JsonResponse({'data': result})


def invoice_detail_search(request, pk):
    search_object = get_object_or_404(Invoice, pk=pk)
    return render(request, 'invoices/example.html', context={'object': search_object})


# search for services

def search_for_service(request):
    if request.headers.get('x-requested-with'):
        input_value = request.POST.get('input_value')
        if len(input_value) < 2:
            result = ''
        else:
            if len(input_value) % 2 != 0:
                input_value = input_value[:-1]
            result = None
            queryset = Service.objects.filter(Q(category__category_name__icontains=input_value) |
                                            Q(title__icontains=input_value) |
                                            Q(price__icontains=input_value) |
                                            Q(detail_text__icontains=input_value)).distinct()

            if len(queryset) > 0:
                data = []
                for element in queryset:
                    item = {'Service': {'pk': element.pk,
                                        'name': element.title,
                                        'price': element.price,
                                        }}
                    data.append(item)
                result = data
            else:
                result = 'No services...'

        return result
        

def service_search(request):
    result = search_for_service(request)

    return JsonResponse({'data': result})


def service_detail_search(request, pk):
    search_object = get_object_or_404(Service, pk=pk)
    return render(request, 'services/example.html', context={'object': search_object})


# search for tickets

def search_for_ticket(request):
    if request.headers.get('x-requested-with'):
        input_value = request.POST.get('input_value')
        if len(input_value) < 2:
            result = ''
        else:
            if len(input_value) % 2 != 0:
                input_value = input_value[:-1]
            result = None
            queryset = Ticket.objects.filter(Q(task_id__icontains=input_value) |
                                            Q(ticket_title__icontains=input_value) |
                                            Q(ticket_text__icontains=input_value) |
                                            Q(comments__text__icontains=input_value) |
                                            Q(created_at__icontains=input_value) |
                                            Q(status__icontains=input_value)).distinct()

            if all([len(queryset) > 0, len(input_value) > 0]):
                data = []
                for element in queryset:
                    item = {'Ticket': {'pk': element.pk,
                                        'task_id': element.task_id,
                                        'title': element.ticket_title,
                                        'date': element.created_at.strftime("%Y-%m-%d"),
                                        }}
                    data.append(item)
                result = data
            else:
                result = 'No tickets...'
        
        return result


def ticket_search(request):
    result = search_for_ticket(request)
        
    return JsonResponse({'data': result})


def ticket_detail_search(request, pk):
    search_object = get_object_or_404(Ticket, pk=pk)
    comments = TicketComments.objects.filter(ticket=pk)
    comments_list = [comm.text for comm in list(comments)]
    return render(request, 'tickets/example.html', context={'object': search_object, 'comments': comments_list})
