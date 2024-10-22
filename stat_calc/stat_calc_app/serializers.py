from .models import CalcMetrics, Calculations, Metrics, AuthUser
from rest_framework import serializers

class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metrics
        fields = ["metric_id", "title", "description", "metric_code", "status", "picture_url"]

class UserSerializer(serializers.ModelSerializer):
   class Meta:
        model = AuthUser
        fields = ["username", "first_name", "last_name", "email"]

class CalcMetricSerializer(serializers.ModelSerializer):
    metric = MetricSerializer()
    class Meta:
        model = CalcMetrics
        fields = ["amount_of_data", "result", "calc_metric_id", "metric"]

class CalcMetricUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalcMetrics
        fields = ["amount_of_data"]

class CalculationSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    moderator = serializers.StringRelatedField()
    class Meta:
        model = Calculations
        fields = ["calc_id", "status", "creation_date", "formation_date", "end_date", "creator", "moderator", "data_for_calc"]

class CalculationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calculations
        fields = ["data_for_calc"]

class CalculationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calculations
        fields = ["status"]

class CalculationDetailSerializer(serializers.ModelSerializer):
    metric = MetricSerializer()
    calc = CalculationSerializer()

    class Meta:
        model = CalcMetrics
        fields = ["calc", "amount_of_data", "result", "calc_metric_id", "metric"] 