from django.contrib import admin
from stat_calc_app import views
from django.urls import include, path
from rest_framework import routers

from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    path(r'metrics/', views.MetricList.as_view(), name='metrics-list'),
    path(r'metrics/<int:metric_id>/', views.MetricDetail.as_view(), name='metric-detail'),
    path(r'metrics/create/', views.MetricCreate.as_view(), name='metric-create'),
    path(r'metrics/<int:metric_id>/update/', views.MetricUpdate.as_view(), name='metric-update'),
    path(r'metrics/<int:metric_id>/delete/', views.MetricDelete.as_view(), name='metric-delete'),
    path(r'metrics/<int:metric_id>/add_picture/', views.MetricAddPicture.as_view(), name='metric-add-picture'),
    path(r'metrics/<int:metric_id>/add_to_calculation/', views.AddToCalculation.as_view(), name='add-to-calculation'),
    path(r'calculations/', views.CalculationList.as_view(), name='calculation-list'),
    path(r'calculations/<int:calculation_id>/', views.CalculationDetail.as_view(), name='calculation-detail'),
    path(r'calculations/<int:calculation_id>/update/', views.CalculationUpdate.as_view(), name='calculation-update'),
    path(r'calculations/<int:calculation_id>/update_status_user/', views.CalculationUpdateStatusUser.as_view(), name='calculation-update-status-user'),
    path(r'calculations/<int:calculation_id>/update_status_admin/', views.CalculationUpdateStatusAdmin.as_view(), name='calculation-update-status-admin'),
    path(r'calculations/<int:calculation_id>/delete/', views.CalculationDelete.as_view(), name='calculation-delete'),
    path(r'calculations/<int:calculation_id>/delete_metric/<int:metric_id>/', views.CalculationDeleteMetric.as_view(), name='calculation-delete-metric'),
    path(r'calculations/<int:calculation_id>/update_metric/<int:metric_id>/', views.CalculationUpdateMetric.as_view(), name='calculation-update-metric'),
    # path(r'users/register/', views.UserRegister.as_view(), name='user-register'),
    # path(r'users/login/', views.UserLogin.as_view(), name='user-login'),
    # path(r'users/logout/', views.UserLogout.as_view(), name='user-logout'),
    # path(r'users/update_profile/', views.UserUpdateProfile.as_view(), name='user-update-profile'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('login/',  views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
