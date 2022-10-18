from django.db import models

import datetime

from django.utils import timezone

from rest_framework import serializers
from rest_framework.fields import Field

# As begin airTemperature and measureTimestamp
#class Parameter(models.Model):
#    parameter_name = models.CharField(max_length=200)
#

 #   def __str__(self):
 #       return self.parameter_name


class env_measure(models.Model):
    def __init__(self, timestamp, air_temperature):
        self.timestamp = timestamp
        self.air_temperature = air_temperature

    # NOTE: Removed the primary key (unique constraint) manually,
    # since we don't want an id column.
    device_id = models.IntegerField()
    timestamp = models.DateTimeField(primary_key=True)
    air_temp = models.FloatField(null=False)
    id = models.IntegerField()
    air_pres = models.FloatField()
    air_hum = models.FloatField()

    #class Meta:
    #    unique_together = ('id', 'timestamp')

class env_measure_30min(models.Model):
    #def __init__(self, timestamp, air_temperature):
    #    self.time = timestamp
    #    self.avg_temp = air_temperature
    device_id = models.IntegerField()
    timestamp = models.DateTimeField(primary_key=True)
    air_temp = models.FloatField(null=False)
    id = models.IntegerField()
    air_pres = models.FloatField()
    air_hum = models.FloatField()

    class Meta:
        managed = False
        db_table = 'envsensor_view_30min'

# create a serializer
class EnvSerializer(serializers.ModelSerializer):
    # initialize fields
    class Meta:
        model = env_measure_30min
        fields = '__all__'
