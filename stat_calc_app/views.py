from django.shortcuts import render, redirect, reverse;
from django.db.models.functions import Coalesce;
from .models import Metrics, Calculations, CalcMetrics;
from django.contrib.auth.models import User;
from django.db.models.functions import Now;
from django.contrib.auth import authenticate, login;
from django.db import connection;

def GetMetrics(request):
    reset_flag = False
    if request.GET:
        metric_name = request.GET.get('metricName').lower()
        metric_filtered = Metrics.objects.filter(title__icontains=metric_name, status='действует')
        reset_flag = True
    else:
        metric_filtered = Metrics.objects.filter(status='действует')
    if Calculations.objects.filter(creator=request.user.id, status='черновик').exists():
        calc_list = int(Calculations.objects.filter(creator=request.user.id, status='черновик')[0].calc_id)
        cnt_metrics = CalcMetrics.objects.filter(calc=calc_list).count()
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
    if Calculations.objects.filter(calc_id=calc_list_id, status='черновик').exists():
        result_list = CalcMetrics.objects.filter(calc=Calculations.objects.filter(
            calc_id=calc_list_id, status='черновик')[0]).select_related('metric', 'calc').all()
        return render(request, 'calc_list.html', {'data': result_list})
    return redirect('metrics')

def AddToCalc(request, metric_id):
    if Calculations.objects.filter(creator=request.user.id, status='черновик').exists():
        calc_list = int(Calculations.objects.filter(creator=request.user.id, status='черновик')[0].calc_id)
        if not CalcMetrics.objects.filter(calc=calc_list, metric=metric_id).exists():
            CalcMetrics.objects.create(calc=Calculations.objects.get(creator=request.user.id, status='черновик'), metric=Metrics.objects.get(metric_id=metric_id))
    else:
        Calculations.objects.create(creation_date=Now(), creator=request.user.id)
        CalcMetrics.objects.create(calc=Calculations.objects.get(creator=request.user.id, status='черновик'), metric=Metrics.objects.get(metric_id=metric_id))
    return redirect('metrics')

def DeleteCalculations(request, calc_list_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE calculations SET status = 'удален' WHERE calc_id = %s", [calc_list_id])
    return redirect('metrics')

def ChangeAmount(request, calc_list_id, calc_metric_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE calc_metrics SET amount_of_data = %s WHERE calc_metric_id = %s", [request.POST.get('inputData'), calc_metric_id])
    return redirect(reverse('calc_list', args=(calc_list_id,)))

def ChangeData(request, calc_list_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE calculations SET data_for_calc = %s WHERE calc_id = %s", [request.POST.get('inputData'), calc_list_id])
    return redirect(reverse('calc_list', args=(calc_list_id,)))