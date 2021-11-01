from django.db import models

# Create your models here.
'''
class Exrate(models.Model):
    date = models.DateField()
    time = models.CharField(max_length = 5)
    currency = models.CharField(max_length = 20)
    cash_buy = models.DecimalField(max_digits = 15, decimal_places = 5)
    cash_sell = models.DecimalField(max_digits = 15, decimal_places = 5)
    spot_buy = models.DecimalField(max_digits = 15, decimal_places = 5)
    spot_sell = models.DecimalField(max_digits = 15, decimal_places = 5)

    def __str__(self):
        return self.currency
'''
class ExrateQuery(models.Model):
    date = models.DateField()
    currency = models.CharField(max_length = 20)
    cash_buy = models.DecimalField(max_digits = 15, decimal_places = 5)
    cash_sell = models.DecimalField(max_digits = 15, decimal_places = 5)
    spot_buy = models.DecimalField(max_digits = 15, decimal_places = 5)
    spot_sell = models.DecimalField(max_digits = 15, decimal_places = 5)

    def __str__(self):
        return self.currency

class BcoExrate(models.Model):
    year = models.IntegerField()
    month = models.CharField(max_length = 2)
    day_r = models.IntegerField()
    currency = models.CharField(max_length = 20)
    bco_buy = models.DecimalField(max_digits = 15, decimal_places = 5)
    bco_sell = models.DecimalField(max_digits = 15, decimal_places = 5)

    def __str__(self):
        return self.currency

class TiptopUser(models.Model):
    account = models.CharField(max_length = 20)
    password = models.CharField(max_length = 20)
    name = models.CharField(max_length = 20)
    c_date = models.DateField()

    def __str__(self):
        return self.name

class Health(models.Model):
    h_date = models.DateField()
    cpf01 = models.CharField(max_length = 8)
    name = models.CharField(max_length = 10)
    phone = models.CharField(max_length = 20)
    status = models.CharField(max_length = 1)
    status0 = models.TextField()
    status1 = models.TextField()
    status2 = models.CharField(max_length = 1)

    def __str__(self):
        return self.cpf01