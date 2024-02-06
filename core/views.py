#from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    if request.method == "GET":
        return first_page(request)
    else:
        return processing_page(request)

def first_page(request):
    return render(request, './get_form.html')

def processing_page(request):
    dep_city = request.POST['dep-city']
    dep_day = request.POST['dep-day']
    arr_day = request.POST['arr-day']
    return render(request, './processing_page.html', {'dep_city':dep_city,
                                                                        'dep_day':dep_day,
                                                                        'arr_day':arr_day})