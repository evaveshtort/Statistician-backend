from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import MetricSerializer, UserSerializer, CalcMetricSerializer, CalculationSerializer, CalculationDetailSerializer, CalculationUpdateSerializer, CalculationStatusSerializer, CalcMetricUpdateSerializer
from .models import Metrics, Calculations, CalcMetrics, CustomUser
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .minio import add_pic, delete_pic
from django.utils import timezone
from datetime import datetime
import statistics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from .permissions import IsAdmin, IsManager
from django.conf import settings
import redis
import uuid

session_id_cookie = openapi.Parameter(
    'session_id', 
    in_=openapi.IN_HEADER, 
    description="Session ID cookie", 
    type=openapi.TYPE_STRING
)

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def create(self, request):
        if self.model_class.objects.filter(email=request.data['email']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            self.model_class.objects.create_user(email=serializer.data['email'],
                                     password=serializer.data['password'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes        
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

class MetricList(APIView):
    model_class = Metrics
    serializer_class = MetricSerializer

    def get(self, request):
        if request.GET:
            metric_name = request.GET.get('metricName').lower()
            metrics = self.model_class.objects.filter(title__icontains=metric_name, status='действует')
        else:
            metrics = self.model_class.objects.filter(status='действует')
        serializer = self.serializer_class(metrics, many=True)

        try:
            user1 = request.user
            if Calculations.objects.filter(creator=user1, status='черновик').exists():
                calc_list = int(Calculations.objects.filter(creator=user1, status='черновик')[0].calc_id)
                cnt_metrics = CalcMetrics.objects.filter(calc=calc_list, status='действует').count()
                if cnt_metrics == 0:
                    calc_list = -1
            else:
                cnt_metrics = 0
                calc_list = -1
        except:
            cnt_metrics = 0
            calc_list = -1
        res = {'draft_calculation_id':calc_list, 'metrics_count':cnt_metrics, 'metrics': serializer.data}
        return Response(res)

class MetricCreate(APIView):
    model_class = Metrics
    serializer_class = MetricSerializer
    @swagger_auto_schema(request_body=MetricSerializer, manual_parameters=[session_id_cookie])
    @method_permission_classes((IsManager,))
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            metric = serializer.save()
            metric.creator = request.user
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

    @method_permission_classes((IsManager,))
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

    @method_permission_classes((IsManager,))
    @swagger_auto_schema(request_body=MetricSerializer, manual_parameters=[session_id_cookie])
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

    @method_permission_classes((IsManager,))
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
        user1 = request.user
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

    @permission_classes([IsAuthenticated])
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'status':'Only for authorized users'}, status=status.HTTP_403_FORBIDDEN)
        user1 = request.user
        date_format = "%Y-%m-%d"
        if user1.is_staff or user1.is_superuser:
            calculations = Calculations.objects.extra(where=["status NOT IN ('черновик', 'удален', 'отклонен')"])
        else:
            calculations = Calculations.objects.filter(creator=user1).extra(where=["status NOT IN ('черновик', 'удален', 'отклонен')"])
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

    @permission_classes([IsAuthenticated])
    def get(self, request, calculation_id):
        if not request.user.is_authenticated:
            return Response({'status':'Only for authorized users'}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.is_staff:
            calc = get_object_or_404(Calculations, creator = request.user, calc_id=calculation_id, status__in=['черновик', 'сформирован', 'завершен', 'отклонен'])
        else:
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

    @swagger_auto_schema(request_body=CalculationUpdateSerializer, manual_parameters=[session_id_cookie])
    def put(self, request, calculation_id):
        calculation = get_object_or_404(self.model_class, calc_id=calculation_id, status='черновик', creator=request.user)
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
        calculation = get_object_or_404(self.model_class, calc_id=calculation_id, creator=request.user)
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

    @method_permission_classes((IsManager,))
    @swagger_auto_schema(request_body=CalculationStatusSerializer, manual_parameters=[session_id_cookie])
    def put(self, request, calculation_id):
        user1 = request.user
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
                        if amount == 1:
                            metric.result = 0
                        else:
                            metric.result = statistics.variance(sample[:amount])
                    elif metric.metric.metric_code == 'exremes':
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
        calculation = get_object_or_404(self.model_class, calc_id=calculation_id, creator=request.user)
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
        calculation = get_object_or_404(Calculations, calc_id=calculation_id, status='черновик', creator=request.user)
        metric = get_object_or_404(Metrics, metric_id = metric_id, status='действует')
        calc_metric = get_object_or_404(self.model_class, calc=calculation, metric=metric, status='действует')
        calc_metric.status = 'удален'
        calc_metric.save()

        return Response(status=status.HTTP_200_OK)
    
class CalculationUpdateMetric(APIView):
    model_class = CalcMetrics
    serializer_class = CalcMetricUpdateSerializer

    @swagger_auto_schema(request_body=CalcMetricUpdateSerializer, manual_parameters=[session_id_cookie])
    def put(self, request, calculation_id, metric_id):
        calculation = get_object_or_404(Calculations, calc_id=calculation_id, status='черновик', creator=request.user)
        metric = get_object_or_404(Metrics, metric_id = metric_id, status='действует')
        calc_metric = get_object_or_404(self.model_class, calc=calculation, metric=metric, status='действует')
        serializer_inp = self.serializer_class(calc_metric, data=request.data, partial=True)

        if serializer_inp.is_valid():
            serializer_inp.save()
            serializer = CalcMetricSerializer(calc_metric)

            return Response(serializer.data['metric'] | {'amount_of_data': serializer.data['amount_of_data'], 'result': serializer.data['result']}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
@swagger_auto_schema(method='post', request_body=UserSerializer, manual_parameters=[session_id_cookie])
@api_view(['Post'])
@permission_classes([AllowAny])
@authentication_classes([])
def login_view(request):
    username = request.data["email"] 
    password = request.data["password"]
    user = authenticate(request, email=username, password=password)
    if user is not None:
        login(request, user)
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, username)

        response = HttpResponse("{'status': 'ok'}")
        response.set_cookie("session_id", random_key)

        return response
    else:
        return Response("{'status': 'error', 'error': 'login failed'}", status=status.HTTP_403_FORBIDDEN)

@api_view(['Post'])
def logout_view(request):
    session_id = request.COOKIES["session_id"]
    if session_id:
        session_storage.delete(session_id)
    logout(request)

    response = Response({'status': 'Success'})
    response.delete_cookie("session_id")
    return response

@swagger_auto_schema(method='put', request_body=UserSerializer, manual_parameters=[session_id_cookie])
@api_view(['Put'])
def update_view(request):
    session_id = request.COOKIES["session_id"]
    if session_id:
        username_old = session_storage.get(session_id).decode('utf-8')
        if username_old:
            user = CustomUser.objects.filter(email=username_old)[0]
            if user:
                response = HttpResponse("{'status': 'ok'}")
                if "email" in request.data.keys():
                    if CustomUser.objects.filter(email=request.data["email"] ).exists():
                        return Response({'status': 'Exist'}, status=400)
                    user.email = request.data["email"] 
                    session_storage.delete(session_id)
                    random_key = str(uuid.uuid4())
                    session_storage.set(random_key, request.data["email"])
                    response.set_cookie("session_id", random_key)
                if "password" in request.data.keys():
                    user.set_password(request.data["password"])
                user.save()
                return response

    return HttpResponse("{'status': 'error', 'error': 'database error'}")

        