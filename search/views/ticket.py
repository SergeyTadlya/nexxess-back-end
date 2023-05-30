from django.http import JsonResponse
from tickets.models import Ticket, TicketComments
from django.db.models import Q
from django.shortcuts import render, get_object_or_404


def search_for_ticket(request):
    if request.headers.get('x-requested-with'):
        input_value = request.POST.get('input_value')
        if len(input_value) < 2:
            result = ''
        else:
            if len(input_value) % 2 != 0:
                input_value = input_value[:-1]
            result = None
            queryset = Ticket.objects.filter(Q(pk__icontains=input_value) |
                                            Q(ticket_title__icontains=input_value) |
                                            Q(ticket_text__icontains=input_value) |
                                            Q(comments__text__icontains=input_value) |
                                            Q(created_at__icontains=input_value) |
                                            Q(status__icontains=input_value)).distinct()

            if all([len(queryset) > 0, len(input_value) > 0]):
                data = []
                for element in queryset:
                    comments = TicketComments.objects.filter(ticket=element.id)
                    comments_list = "\n".join([comm.text for comm in list(comments)])
                    item = {'Ticket': {'pk': element.pk,
                                        'id': element.pk,
                                        'title': element.ticket_title,
                                        'description': element.ticket_text,
                                        'comments': comments_list,
                                        'date': element.created_at.strftime("%Y-%m-%d"),
                                        'status': element.status
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
    comments_list = "\n".join([comm.text for comm in list(comments)])
    return render(request, 'tickets/example.html', context={'object': search_object, 'comments': comments_list})  # 'detail.html' ???
