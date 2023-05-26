from django.http import JsonResponse
from tickets.models import Ticket
from django.db.models import Q
from django.shortcuts import render


def ticket_search(request):
    # if request.is_ajax():
    input = ''
    # input = request.POST.get('input')  # input will return from search form
    try:
        input = request.GET.get("input", "")
    except AttributeError as er:
        print(er)
    result = None
    queryset = Ticket.objects.filter(Q(pk__icontains=input) |
                                     Q(ticket_title__icontains=input) |
                                     Q(ticket_text__icontains=input) |
                                     Q(comments__text__icontains=input) |
                                     Q(created_at__icontains=input) |
                                     Q(status__icontains=input))

    if all([len(queryset) > 0, len(input) > 0]):
        data = []
        for element in queryset:
            item = {'Ticket': {'pk': element.pk,
                                'id': element.pk,
                                'title': element.ticket_title,
                                'description': element.ticket_title,
                                'comments': element.comments.core_filters.get('ticket').ticket_text,
                                'date': element.created_at,
                                'status': element.status
                                }}
            data.append(item)
        result = data
    else:
        result = ''
    
    return JsonResponse({'data': result})

    # return JsonResponse({})


def ticket_detail_search(request, pk):
    search_object = Ticket.objects.get(pk=pk)
    return render(request, 'detail.html', context={'object': search_object})  # 'detail.html' ???