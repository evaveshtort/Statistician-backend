"""
URL configuration for stat_calc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from stat_calc_app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.GetMetrics, name='metrics'),
    path('add_calculations/<int:metric_id>', views.AddToCalc, name='add_calculations'),
    path('metric/<int:id>/', views.GetMetric, name='metric_url'),
    path('calc_list/<int:calc_list_id>/', views.GetCalcList, name='calc_list'),
    path('calc_list/<int:calc_list_id>/delete_calculations', views.DeleteCalculations, name='delete_calculations'),
]
