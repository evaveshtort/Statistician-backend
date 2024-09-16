from django.shortcuts import render
from datetime import date

# Create your views here.
def GetMetrics(request):
    return render(request, 'main_page.html', {'data' : {
        'current_date': date.today(),
        'metrics': [
            {'title': 'Математическое ожидание', 'id': 1, 'picture':'https://127.0.0.1:9000/cardpictures/mathematical_expectation.png'},
            {'title': 'Дисперсия', 'id': 2, 'picture':'https://127.0.0.1:9000/cardpictures/dispersion.png'},
            {'title': 'Pvalue', 'id': 3, 'picture':'https://127.0.0.1:9000/cardpictures/pvalue.png'},
        ]
    }})

def GetMetric(request, id):
    return render(request, 'metric.html', {'data' : {
        'current_date': date.today(),
        'id': id
    }})