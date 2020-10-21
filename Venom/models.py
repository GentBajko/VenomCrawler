from django.contrib.auth.forms import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.contrib.auth.models import models


class Crawler(models.Model):
    username = models.CharField(max_length=50)
    creation_date = models.DateTimeField()
    name = models.CharField(max_length=30)
    starting_url = models.CharField(max_length=50)
    column_names = SimpleArrayField(models.CharField(max_length=50))
    xpaths: SimpleArrayField(models.CharField(max_length=50))
    next_xpath = models.CharField(max_length=50)
    product_xpath = models.CharField(max_length=50)
    url_queries = SimpleArrayField(models.CharField(max_length=50))
    page_query = models.CharField(max_length=50)
    page_steps = models.IntegerField()
    last_page_xpath = models.CharField(max_length=50)
    last_page_arrow = models.CharField(max_length=50)
    search_xpath = models.CharField(max_length=50)
    search_terms = SimpleArrayField(models.CharField(max_length=50))
    load_more = models.CharField(max_length=50)
    regex = models.JSONField()
    predefined_url_list = SimpleArrayField(models.CharField(max_length=50))
    error_xpaths = SimpleArrayField(models.CharField(max_length=50))
    chunksize = models.IntegerField()

    def __str__(self):
        return self.name
