from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager


class CalcMetrics(models.Model):
    calc = models.ForeignKey('Calculations', models.DO_NOTHING)
    metric = models.ForeignKey('Metrics', models.DO_NOTHING)
    amount_of_data = models.IntegerField(default=1)
    result = models.FloatField(blank=True, null=True)
    calc_metric_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=50, default='действует')

    class Meta:
        managed = False
        db_table = 'calc_metrics'
        unique_together = (('calc', 'metric'),)


class Calculations(models.Model):
    calc_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=30, default='черновик')
    creation_date = models.DateTimeField()
    formation_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey('CustomUser', models.DO_NOTHING, related_name='creator')
    moderator = models.ForeignKey('CustomUser', models.DO_NOTHING, related_name='moderator')
    data_for_calc = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'calculations'


class Metrics(models.Model):
    metric_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    picture_url = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True)
    status = models.CharField(max_length=20, default='действует')
    metric_code = models.CharField(max_length=50)
    creator = models.ForeignKey('CustomUser', models.DO_NOTHING, null=True)

    class Meta:
        managed = False
        db_table = 'metrics'

class NewUserManager(UserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email) 
        user = self.model(email=email, **extra_fields) 
        user.set_password(password)
        user.save(using=self.db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(("email адрес"), unique=True)
    password = models.CharField(max_length=200, verbose_name="Пароль")    
    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")
    date_joined = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    objects =  NewUserManager()

# class AuthUser(models.Model):
#     id = models.AutoField(primary_key = True)
#     password = models.CharField(max_length=128)
#     last_login = models.DateTimeField(blank=True, null=True)
#     is_superuser = models.BooleanField(default=False)
#     username = models.CharField(unique=True, max_length=150)
#     last_name = models.CharField(max_length=150)
#     email = models.CharField(max_length=254)
#     is_staff = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     date_joined = models.DateTimeField(auto_now=True)
#     first_name = models.CharField(max_length=150)

#     def __str__(self):
#         return f'{self.username}'

#     class Meta:
#         managed = False
#         db_table = 'auth_user'


