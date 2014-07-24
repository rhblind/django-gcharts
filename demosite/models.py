from django.db import models
from gcharts import GChartsManager


class GeoData(models.Model):
    """
    A model which contains data for the GeoChart
    """

    objects = GChartsManager()

    country_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    population = models.PositiveIntegerField()
    fertility_rate = models.FloatField()
    

class OtherData(models.Model):
    """
    A model which contains some other random data
    """

    objects = GChartsManager()

    name = models.CharField(max_length=20)
    number1 = models.IntegerField()
    number2 = models.IntegerField()
    date = models.DateField()
