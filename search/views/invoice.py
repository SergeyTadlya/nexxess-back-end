from django.http import JsonResponse
from invoices.models import Invoice
from django.db.models import Q
from django.shortcuts import render, get_object_or_404


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
                                            Q(status__abbreviation__icontains=input_value)).distinct()

            if all([len(queryset) > 0, len(input_value) > 0]):
                data = []
                for element in queryset:
                    item = {'Invoice': {'pk': element.pk,
                                        'number': element.invoice_id,
                                        'date': element.created_at.strftime("%Y-%m-%d"),
                                        'price': element.price,
                                        'status': element.status.abbreviation,
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
    return render(request, 'invoices/example.html', context={'object': search_object})  # 'detail.html' ???