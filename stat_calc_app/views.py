from django.shortcuts import render
from datetime import date

# Create your views here.
def GetMetrics(request):
    return render(request, 'cards.html', {'data' : {
        'current_date': date.today(),
        'metrics': [
            {'title': 'Математическое ожидание', 'id': 1, 'picture':"http://127.0.0.1:9000/cardpictures/mathematical_expectation.png",
             'description':'Представляет собой среднее значение случайной величины и помогает предсказать, какие значения можно ожидать в будущем'},
            {'title': 'Дисперсия', 'id': 2, 'picture':"http://127.0.0.1:9000/cardpictures/dispersion.png",
             'description':'Мера разброса случайной величины относительно её математического ожидания'},
            {'title': 'Pvalue', 'id': 3, 'picture':"http://127.0.0.1:9000/cardpictures/pvalue.png",
             'description':'Величина, применяемая при статистической проверке гипотиз'},
        ]
    }})

def GetMetric(request, id):
    return render(request, 'metric.html', {'data' : {
        'current_date': date.today(),
        'id': id
    }})