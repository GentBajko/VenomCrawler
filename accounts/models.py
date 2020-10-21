from django.contrib.auth.models import models


class Registration(models.Model):
    name = models.CharField(max_length=30)
    middlename = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    # birthday = models.DateField()
    username = models.CharField(max_length=30)
    # email = models.EmailField()
    country = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    confirm_password = models.CharField(max_length=30)
    company = models.CharField(max_length=30)
