from django.contrib import admin

from .models import CalcMetrics, Calculations, Metrics

admin.site.register(CalcMetrics)
admin.site.register(Calculations)
admin.site.register(Metrics)
