from django.http import JsonResponse
from services.models import Service
from django.db.models import Q
from django.shortcuts import render, get_object_or_404


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
                                        'category': element.category.category_name,
                                        'name': element.title,
                                        'price': element.price,
                                        'details': element.detail_text,
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
    return render(request, 'services/example.html', context={'object': search_object})  # 'detail.html' ???