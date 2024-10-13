from .models import CalcMetrics, Calculations, Metrics
from rest_framework import serializers

class CalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calculations
        fields = []

class CalcMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalcMetrics
        fields = []

class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metrics
        fields = ["title", "description", "metric_code"]