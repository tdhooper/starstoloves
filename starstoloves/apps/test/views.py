from django.shortcuts import render

def results(request):
    return render(request, 'results.html')