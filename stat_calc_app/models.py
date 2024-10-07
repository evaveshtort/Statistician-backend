from django.db import models


class CalcMetrics(models.Model):
    calc = models.ForeignKey('Calculations', models.DO_NOTHING)
    metric = models.ForeignKey('Metrics', models.DO_NOTHING)
    amount_of_data = models.IntegerField()
    result = models.FloatField(blank=True, null=True)
    calc_metric_id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'calc_metrics'
        unique_together = (('calc', 'metric'),)


class Calculations(models.Model):
    calc_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=30)
    creation_date = models.DateTimeField()
    formation_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    creator = models.CharField(max_length=50)
    moderator = models.CharField(max_length=50, blank=True, null=True)
    data_for_calc = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'calculations'


class Metrics(models.Model):
    metric_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    picture_url = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'metrics'