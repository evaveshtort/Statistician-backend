from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import MetricSerializer, UserSerializer, CalcMetricSerializer, CalculationSerializer, CalculationDetailSerializer, CalculationUpdateSerializer, CalculationStatusSerializer, CalcMetricUpdateSerializer
from .models import Metrics, Calculations, CalcMetrics, AuthUser
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .minio import add_pic, delete_pic
from django.utils import timezone
from datetime import datetime
from django.http import QueryDict
import statistics

def user():
    try:
        user1 = AuthUser.objects.get(id=1)[0]
    except:
        user1 = AuthUser(id=1, first_name="Ева", last_name="Вешторт", password=1234, username="admin")
        user1.save()
    return user1

class MetricList(APIView):
    model_class = Metrics
    serializer_class = MetricSerializer

    def get(self, request):
        user1 = user()
        if request.GET:
            metric_name = request.GET.get('metricName').lower()
            metrics = self.model_class.objects.filter(title__icontains=metric_name, status='действует')
        else:
            metrics = self.model_class.objects.filter(status='действует')
        if Calculations.objects.filter(creator=user1, status='черновик').exists():
            calc_list = int(Calculations.objects.filter(creator=user1, status='черновик')[0].calc_id)
            cnt_metrics = CalcMetrics.objects.filter(calc=calc_list, status='действует').count()
            if cnt_metrics == 0:
                calc_list = -1
        else:
            cnt_metrics = 0
            calc_list = -1
        serializer = self.serializer_class(metrics, many=True)
        res = {'draft_calculation_id':calc_list, 'metrics_count':cnt_metrics, 'metrics': serializer.data}
        return Response(res)

class MetricCreate(APIView):
    model_class = Metrics
    serializer_class = MetricSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            metric = serializer.save()
            user1 = user()
            metric.creator = user1
            metric.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MetricDetail(APIView):
    model_class = Metrics
    serializer_class = MetricSerializer

    def get(self, request, metric_id):
        metric = get_object_or_404(self.model_class, metric_id=metric_id, status='действует')
        serializer = self.serializer_class(metric)
        return Response(serializer.data)
    
class MetricAddPicture(APIView):
    model_class = Metrics
    serializer_class = MetricSerializer

    def post(self, request, metric_id):
        metric = get_object_or_404(self.model_class, metric_id=metric_id)
        pic = request.FILES.get("pic")
        pic_result = add_pic(metric, pic)
        if 'error' in pic_result.data:    
            return pic_result
        return Response(status=status.HTTP_201_CREATED)
    
class MetricUpdate(APIView):
    model_class = Metrics
    serializer_class = MetricSerializer

    def put(self, request, metric_id):
        metric = get_object_or_404(self.model_class, metric_id=metric_id)
        serializer = self.serializer_class(metric, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MetricDelete(APIView):
    model_class = Metrics
    serializer_class = MetricSerializer

    def delete(self, request, metric_id):
        metric = get_object_or_404(self.model_class, metric_id=metric_id)
        delete_pic(metric)
        metric.status = 'удален'
        metric.save()
        for calc_metric in CalcMetrics.objects.filter(metric=metric):
            calc_metric.status = 'удален'
            calc_metric.save()
        metrics = self.model_class.objects.filter(status='действует')
        serializer = self.serializer_class(metrics, many=True)
        return Response(serializer.data)
    
class AddToCalculation(APIView):
    model_class = CalcMetrics
    serializer_class = CalcMetricSerializer

    def post(self, request, metric_id):
        if Metrics.objects.filter(metric_id=metric_id, status='действует').count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user1 = user()
        if Calculations.objects.filter(creator=user1, status='черновик').exists():
            calc_list = int(Calculations.objects.filter(creator=user1, status='черновик')[0].calc_id)
            if not self.model_class.objects.filter(calc=calc_list, metric=metric_id).exists():
                self.model_class.objects.create(calc=Calculations.objects.get(creator=user1, status='черновик'), metric=Metrics.objects.get(metric_id=metric_id))
            else:
                calc_metric = self.model_class.objects.get(calc=calc_list, metric=metric_id)
                calc_metric.status = 'действует'
                calc_metric.save()
        else:
            Calculations.objects.create(creation_date=timezone.now(), creator=user1)
            self.model_class.objects.create(calc=Calculations.objects.get(creator=user1, status='черновик'), metric=Metrics.objects.get(metric_id=metric_id))
        metrics = self.model_class.objects.filter(calc=Calculations.objects.filter(
            creator=user1, status='черновик')[0], status='действует')
        serializer = self.serializer_class(metrics, many=True)
        res = []
        for i in serializer.data:
            res.append({**i['metric'], **{'amount_of_data': i['amount_of_data'], 'result': i['result']}})
        return Response(res, status=status.HTTP_201_CREATED)
    
class CalculationList(APIView):
    model_class = Calculations
    serializer_class = CalculationSerializer

    def get(self, request):
        date_format = "%Y-%m-%d"
        calculations = Calculations.objects.extra(where=["status NOT IN ('черновик', 'удален')"])
        start_date = datetime(2024, 1, 1)
        end_date = timezone.now()
        if request.GET.get('dateStart'):
            start_date = datetime.strptime(request.GET.get('dateStart'), date_format).date()
        if request.GET.get('dateEnd'):
            end_date = datetime.strptime(request.GET.get('dateEnd'), date_format).date()
        calculations = calculations.filter(formation_date__gte=start_date, formation_date__lt=end_date)
        if request.GET.get('status'):
            calculations = calculations.filter(status=request.GET.get('status'))
        serializer = self.serializer_class(calculations, many=True)
        return Response(serializer.data)

class CalculationDetail(APIView):
    model_class = CalcMetrics
    serializer_class = CalculationDetailSerializer

    def get(self, request, calculation_id):
        calc = get_object_or_404(Calculations, calc_id=calculation_id, status__in=['черновик', 'сформирован', 'завершен', 'отклонен'])
        calculation = self.model_class.objects.filter(calc=calc, status='действует')
        if calculation.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(calculation, many=True)
        try:
            res = serializer.data[0]['calc'] | {'metrics': [{'amount_of_data':x['amount_of_data'], 'result':x['result']} | x['metric'] for x in serializer.data]}
        except:
            res = serializer.data['calc'] | {'metrics': [{'amount_of_data':serializer.data['amount_of_data'], 'result':serializer.data['result']} | serializer.data['metric']]}
        return Response(res)
    
class CalculationUpdate(APIView):
    model_class = Calculations
    serializer_class = CalculationUpdateSerializer

    def put(self, request, calculation_id):
        calculation = get_object_or_404(self.model_class, calc_id=calculation_id, status='черновик')
        serializer_inp = self.serializer_class(calculation, data=request.data, partial=True)

        if serializer_inp.is_valid():
            serializer_inp.save()
            serializer = CalculationSerializer(calculation)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CalculationUpdateStatusUser(APIView):
    model_class = Calculations
    serializer_class = CalculationSerializer

    def put(self, request, calculation_id):
        calculation = get_object_or_404(self.model_class, calc_id=calculation_id)
        if calculation.status != 'черновик' or not calculation.data_for_calc:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        calculation.status = 'сформирован'
        calculation.formation_date = timezone.now()
        calculation.save()
        serializer = CalculationSerializer(calculation)
        return Response(serializer.data)
    
class CalculationUpdateStatusAdmin(APIView):
    model_class = Calculations
    serializer_class = CalculationStatusSerializer

    def put(self, request, calculation_id):
        user1 = user()
        calculation = get_object_or_404(self.model_class, calc_id=calculation_id)
        if calculation.status != 'сформирован' or not calculation.data_for_calc:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer_inp = self.serializer_class(calculation, data=request.data, partial=True)
        if serializer_inp.is_valid():
            try: 
                serializer_inp.save()
                if calculation.status not in ['завершен', 'отклонен']:
                    calculation.status = 'сформирован'
                    calculation.save()
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            calculation.moderator = user1
            calculation.end_date = timezone.now()
            calculation.save()

            if calculation.status == 'завершен':
                sample = [float(x) for x in calculation.data_for_calc.split(' ')]
                for metric in CalcMetrics.objects.filter(calc=calculation, status='действует'):
                    amount = min(len(sample), metric.amount_of_data)
                    if metric.metric.metric_code == 'mathematical_expectation':
                        metric.result = statistics.mean(sample[:amount])
                    elif metric.metric.metric_code == 'dispersion':
                        metric.result = statistics.variance(sample[:amount])
                    elif metric.metric.metric_code == 'extremes':
                        metric.result = max(sample[:amount])
                    elif metric.metric.metric_code == 'percentiles':
                        metric.result = statistics.median(sample[:amount])
                    elif metric.metric.metric_code == 'mode':
                        metric.result = statistics.mode(sample[:amount])
                    else:
                        continue
                    metric.save()
            
            calculations = CalcMetrics.objects.filter(calc=calculation)
            serializer = CalculationDetailSerializer(calculations, many=True)
            try:
                res = serializer.data[0]['calc'] | {'metrics': [{'amount_of_data':x['amount_of_data'], 'result':x['result']} | x['metric'] for x in serializer.data]}
            except:
                res = serializer.data['calc'] | {'metrics': [{'amount_of_data':serializer.data['amount_of_data'], 'result':serializer.data['result']} | serializer.data['metric']]}
            return Response(res)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CalculationDelete(APIView):
    model_class = Calculations
    serializer_class = MetricSerializer

    def delete(self, request, calculation_id):
        calculation = get_object_or_404(self.model_class, calc_id=calculation_id)
        if calculation.status == 'черновик':
            calculation.status = 'удален'
            calculation.formation_date = timezone.now()
            calculation.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
class CalculationDeleteMetric(APIView):
    model_class = CalcMetrics
    serializer_class = CalculationDetailSerializer

    def delete(self, request, calculation_id, metric_id):
        calculation = get_object_or_404(Calculations, calc_id=calculation_id, status='черновик')
        metric = get_object_or_404(Metrics, metric_id = metric_id, status='действует')
        calc_metric = get_object_or_404(self.model_class, calc=calculation, metric=metric, status='действует')
        calc_metric.status = 'удален'
        calc_metric.save()

        return Response(status=status.HTTP_200_OK)
    
class CalculationUpdateMetric(APIView):
    model_class = CalcMetrics
    serializer_class = CalcMetricUpdateSerializer

    def put(self, request, calculation_id, metric_id):
        calculation = get_object_or_404(Calculations, calc_id=calculation_id, status='черновик')
        metric = get_object_or_404(Metrics, metric_id = metric_id, status='действует')
        calc_metric = get_object_or_404(self.model_class, calc=calculation, metric=metric, status='действует')
        serializer_inp = self.serializer_class(calc_metric, data=request.data, partial=True)

        if serializer_inp.is_valid():
            serializer_inp.save()
            serializer = CalcMetricSerializer(calc_metric)

            return Response(serializer.data['metric'] | {'amount_of_data': serializer.data['amount_of_data'], 'result': serializer.data['result']}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserRegister(APIView):
    model_class = AuthUser
    def post(self, request):
        return Response(status=status.HTTP_200_OK)

class UserLogin(APIView):
    model_class = AuthUser
    def post(self, request):
        return Response(status=status.HTTP_200_OK)

class UserLogout(APIView):
    model_class = AuthUser
    def post(self, request):
        return Response(status=status.HTTP_200_OK)

class UserUpdateProfile(APIView):
    model_class = AuthUser
    serializer_class = UserSerializer

    def put(self, request):
        user1 = user()
        serializer_inp = self.serializer_class(user1, data=request.data, partial=True)
        if serializer_inp.is_valid():
            serializer_inp.save()
        return Response(status=status.HTTP_200_OK)
        