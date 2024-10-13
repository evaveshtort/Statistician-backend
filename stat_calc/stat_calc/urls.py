from django.contrib import admin
from stat_calc_app import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'metrics/', views.MetricList.as_view(), name='metrics-list'),
    path(r'metrics/<int:pk>/', views.MetricDetail.as_view(), name='metrics-detail'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
]
