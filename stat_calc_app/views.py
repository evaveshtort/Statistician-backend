from django.shortcuts import render
from .models import Metrics, Calculations, CalcMetrics;
from django.contrib.auth.models import User;

def GetMetrics(request):
    reset_flag = False
    if request.GET:
        metric_name = request.GET.get('metricName').lower()
        metric_filtered = Metrics.objects.filter(title__icontains=metric_name)
        reset_flag = True
    else:
        metric_filtered = Metrics.objects.all()
    if Calculations.objects.filter(creator=request.user.id, status='черновик').exists():
        calc_list = int(Calculations.objects.filter(creator=request.user.id, status='черновик')[0].calc_id)
        cnt_metrics = CalcMetrics.objects.filter(calc_id=calc_list).count()
    else:
        cnt_metrics = 0
        calc_list = -1
    return render(request, 'metrics.html', {'data' : {
        'metrics': metric_filtered,
        'count_metrics_in_calc_list': cnt_metrics,
        'calc_list_id': calc_list,
        'reset_flag': reset_flag
    }})

def GetMetric(request, id):
    target_metric = Metrics.objects.filter(metric_id=id, status='действует')[0]
    return render(request, 'metric.html', {'data' : target_metric})

def GetCalcList(request, calc_list_id):
    result_list = []
    CalcMetrics.objects.filter(calc=calc_list_id).select_related(Metrics).values('title', 'picture_url', 'metric_id')
    return render(request, 'calc_list.html', {'data': result_list})