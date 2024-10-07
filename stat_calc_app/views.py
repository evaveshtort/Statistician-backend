from django.shortcuts import render

metric_list = [
            {'title': 'Математическое ожидание', 'id': 1, 'picture':"http://127.0.0.1:9000/cardpictures/mathematical_expectation.png",
             'longDesc': 'Математическое ожидание является одним из важнейших понятий теории вероятности, поскольку может служить в качестве усредненной оценки случайной величины. С его помощью можно прогнозировать оценку значения некоторого случайного признака при наличии достаточно большого числа наблюдений.'},
            {'title': 'Дисперсия', 'id': 2, 'picture':"http://127.0.0.1:9000/cardpictures/dispersion.png",
             'longDesc': 'Дисперсия в статистике — это мера, которая показывает разброс между результатами. Если все они близки к среднему, дисперсия низкая. А если результаты сильно различаются — высокая'},
            {'title': 'Экстремумы', 'id': 3, 'picture':"http://127.0.0.1:9000/cardpictures/extremes.png",
             'longDesc':'Экстремумы - максимальное и минимальное значения выборки.'},
            {'title': 'Процентили', 'id': 4, 'picture':"http://127.0.0.1:9000/cardpictures/percentiles.png",
             'longDesc':'Процентили делят всю выборку на определенные части. Например, пятый процентиль охватывает 5% объема выборки. Предположим, показатель Ивана равен пятому процентилю. Это означает, что Иван написал тест лучше, чем 5% студентов.'},
            {'title': 'Мода', 'id': 5, 'picture':"http://127.0.0.1:9000/cardpictures/mode.png",
             'longDesc':'Мода — одно или несколько значений во множестве наблюдений, которое встречается наиболее часто (мода = типичность).'},
        ]

calc_list_info = {'calc_list_id': 1, 'metrics': [1, 2]}

def GetMetrics(request):
    reset_flag = False
    if request.GET:
        metric_name = request.GET.get('metricName').lower()
        metric_filtered = [x for x in metric_list if metric_name in x['title'].lower()]
        reset_flag = True
    else:
        metric_filtered = metric_list
    return render(request, 'metrics.html', {'data' : {
        'metrics': metric_filtered,
        'count_metrics_in_calc_list': len(calc_list_info['metrics']),
        'calc_list_id': calc_list_info['calc_list_id'],
        'reset_flag': reset_flag
    }})

def GetMetric(request, id):
    for metric in metric_list:
        if metric['id'] == id:
            target_metric = metric
            break
    return render(request, 'metric.html', {'data' : target_metric})

def GetCart(request, calc_list_id):
    result_list = []
    if calc_list_info['calc_list_id'] == calc_list_id:
        for j in metric_list:
            if j['id'] in calc_list_info['metrics']:
                result_list.append({'metric_name': j['title'], 'picture': j['picture'], 'metric_id': j['id']})
    return render(request, 'calc_list.html', {'data': result_list})