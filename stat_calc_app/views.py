from django.shortcuts import render
from datetime import date

data_list = [
            {'title': 'Математическое ожидание', 'id': 1, 'picture':"http://127.0.0.1:9000/cardpictures/mathematical_expectation.png",
             'description':'Представляет собой среднее значение случайной величины и помогает предсказать, какие значения можно ожидать в будущем',
             'longDesc': 'Математическое ожидание является одним из важнейших понятий теории вероятности, поскольку может служить в качестве усредненной оценки случайной величины. С его помощью можно прогнозировать оценку значения некоторого случайного признака при наличии достаточно большого числа наблюдений.'},
            {'title': 'Дисперсия', 'id': 2, 'picture':"http://127.0.0.1:9000/cardpictures/dispersion.png",
             'description':'Мера разброса случайной величины относительно её математического ожидания',
             'longDesc': 'Дисперсия в статистике — это мера, которая показывает разброс между результатами. Если все они близки к среднему, дисперсия низкая. А если результаты сильно различаются — высокая'},
            {'title': 'Pvalue', 'id': 3, 'picture':"http://127.0.0.1:9000/cardpictures/pvalue.png",
             'description':'Величина, применяемая при статистической проверке гипотиз',
             'longDesc':'Значимая вероятность — это величина, применяемая при статистической проверке гипотез. Представляет собой вероятность того, что значение проверочной статистики используемого критерия (t-статистики Стьюдента, F-статистики Фишера и т.д.), вычисленное по выборке, превысит установленное p-значение.'},
            {'title': 'Процентили', 'id': 4, 'picture':"http://127.0.0.1:9000/cardpictures/percentiles.png",
             'description':'Значения, которые случайная величина не превышает с заданной вероятностью',
             'longDesc':'Процентили делят всю выборку на определенные части. Например, пятый процентиль охватывает 5% объема выборки. Предположим, показатель Ивана равен пятому процентилю. Это означает, что Иван написал тест лучше, чем 5% студентов'},
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
    result_list = []
    for i in carts_info:
        if i['cart_id'] == cart_id:
            for j in data_list:
                if j['id'] == i['metric_id']:
                    result_list.append({'metric_name': j['title'], 'picture': j['picture'], 'metric_id': j['id'], 'data_for_calc': i['data_for_calc']})
    return render(request, 'cart.html', {'data': result_list})