from django.http import JsonResponse
from invoices.models import Invoice
from django.db.models import Q
from django.shortcuts import render


def invoice_search(request):
    # if request.is_ajax():
    input = ''
    # input = request.POST.get('input')  # input will return from search form
    try:
        input = request.GET.get("input", "")
    except AttributeError as er:
        print(er)
    result = None
    queryset = Invoice.objects.filter(Q(invoice_id__icontains=input) |
                                      Q(created_at__icontains=input) |
                                      Q(price__icontains=input) |
                                      Q(status__abbreviation__icontains=input))

    if all([len(queryset) > 0, len(input) > 0]):
        data = []
        for element in queryset:
            item = {'Invoice': {'pk': element.pk,
                                'number': element.invoice_id,
                                'date': element.created_at,
                                'price': element.price,
                                'status': element.status.abbreviation,
                                }}
            data.append(item)
        result = data
    else:
        result = ''
    
    return JsonResponse({'data': result})

    # return JsonResponse({})


def invoice_detail_search(request, pk):
    search_object = Invoice.objects.get(pk=pk)
    return render(request, 'detail.html', context={'object': search_object})  # 'detail.html' ???