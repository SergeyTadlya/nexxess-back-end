from django.http import JsonResponse
from services.models import Service
from django.db.models import Q
from django.shortcuts import render


def service_search(request):
    # if request.is_ajax():
    input = ''
    # input = request.POST.get('input')  # input will return from search form
    try:
        input = request.GET.get("input", "")
    except AttributeError as er:
        print(er)
    result = None
    queryset = Service.objects.filter(Q(category__category_name__icontains=input) |
                                      Q(title__icontains=input) |
                                      Q(price__icontains=input) |
                                      Q(detail_text__icontains=input))

    if all([len(queryset) > 0, len(input) > 0]):
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
        result = ''
    
    return JsonResponse({'data': result})

    # return JsonResponse({})


def service_detail_search(request, pk):
    search_object = Service.objects.get(pk=pk)
    return render(request, 'detail.html', context={'object': search_object})  # 'detail.html' ???