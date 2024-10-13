from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import MetricSerializer
from .models import Metrics, Calculations, CalcMetrics
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .minio import add_pic, delete_pic
import json

class MetricList(APIView):
    model_class = Metrics
    serializer_class = MetricSerializer

    def get(self, request, format=None):
        if request.GET:
            metric_name = request.GET.get('metricName').lower()
            metrics = self.model_class.objects.filter(title__icontains=metric_name, status='действует')
        else:
            metrics = self.model_class.objects.filter(status='действует')
        if Calculations.objects.filter(creator=request.user.id, status='черновик').exists():
            calc_list = int(Calculations.objects.filter(creator=request.user.id, status='черновик')[0].calc_id)
            cnt_metrics = CalcMetrics.objects.filter(calc=calc_list).count()
        else:
            cnt_metrics = 0
            calc_list = -1
        serializer = self.serializer_class(metrics, many=True)
        res = [{'calc_list_id':calc_list, 'cnt_metrics':cnt_metrics}] + serializer.data
        return Response(res)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MetricDetail(APIView):
    model_class = Metrics
    serializer_class = MetricSerializer

    def get(self, request, pk, format=None):
        metric = get_object_or_404(self.model_class, metric_id=pk, status='действует')
        serializer = self.serializer_class(metric)
        return Response(serializer.data)
    
    def post(self, request, pk, format=None):
        metric = get_object_or_404(self.model_class, metric_id=pk)
        pic = request.FILES.get("pic")
        pic_result = add_pic(metric, pic)
        if 'error' in pic_result.data:    
            return pic_result
        return Response(status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        metric = get_object_or_404(self.model_class, metric_id=pk)
        serializer = self.serializer_class(metric, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        metric = get_object_or_404(self.model_class, metric_id=pk)
        delete_pic(metric)
        metric.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)