from django.shortcuts import render
from datetime import date

data_list = [
            {'title': 'Математическое ожидание', 'id': 1, 'picture':"http://127.0.0.1:9000/cardpictures/mathematical_expectation.png",
             'description':'Представляет собой среднее значение случайной величины и помогает предсказать, какие значения можно ожидать в будущем'},
            {'title': 'Дисперсия', 'id': 2, 'picture':"http://127.0.0.1:9000/cardpictures/dispersion.png",
             'description':'Мера разброса случайной величины относительно её математического ожидания'},
            {'title': 'Pvalue', 'id': 3, 'picture':"http://127.0.0.1:9000/cardpictures/pvalue.png",
             'description':'Величина, применяемая при статистической проверке гипотиз'},
            {'title': 'Процентили', 'id': 4, 'picture':"http://127.0.0.1:9000/cardpictures/percentiles.png",
             'description':'Значения, которые случайная величина не превышает с заданной вероятностью'},
        ]

carts_info = [
    {'cart_id': 1, 'metric_id': 1, 'data_for_calc': [2, 35, 18, 150]},
    {'cart_id': 1, 'metric_id': 2, 'data_for_calc': [2, 35, 18, 150]}
]

users_info = [
    {'user_id': 1, 'cart_id': 1}
]

def GetMetrics(request):
    user = 1
    for u in users_info:
        if u['user_id'] == user:
            cart = u['cart_id']
            break
    reset_flag = False
    if request.GET:
        query = request.GET.get('metricName').lower()
        data_filtered = [x for x in data_list if query in x['title'].lower()]
        reset_flag = True
    else:
        data_filtered = data_list
    return render(request, 'cards.html', {'data' : {
        'metrics': data_filtered,
        'count_metrics_in_cart': len([x for x in carts_info if x['cart_id']==cart]),
        'cart_id': cart,
        'reset_flag': reset_flag
    }})

def GetMetric(request, id):
    for metric in data_list:
        if metric['id'] == id:
            target_metric = metric
            break
    return render(request, 'metric.html', {'data' : target_metric})

def GetCart(request, cart_id):
    return render(request, 'cart.html')