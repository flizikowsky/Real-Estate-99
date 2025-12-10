from django.db import models

from django.contrib.auth.models import User
from properties.models import Property


class Customer(models.Model):
	user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
	email = models.CharField(max_length=150, null=True)
	model_name = models.CharField(max_length=50, null=True, blank=True)
	
	last_property_type = models.CharField(max_length=45, null=True, blank=True)
	last_sell_type = models.CharField(max_length=45, null=True, blank=True)
	
	saved = models.ManyToManyField(Property, related_name='saved', blank=True)
	not_interested = models.ManyToManyField(Property, related_name='not_interested', blank=True)
	picked = models.ManyToManyField(Property, related_name='picked', blank=True)
	
	class Meta:
		db_table = 'customers'

	def __str__(self):
		return self.email

class Filter(models.Model):
	username = models.CharField(max_length=150)
	location = models.CharField(max_length=50, null=True, blank=True)
	min_price = models.IntegerField(null=True, blank=True)
	max_price = models.IntegerField(null=True, blank=True)
	min_surface = models.IntegerField(null=True, blank=True)
	max_surface = models.IntegerField(null=True, blank=True)
	type_property = models.CharField(max_length=50, null=True, blank=True)
	type_sell = models.CharField(max_length=50, null=True, blank=True)
	
	class Meta:
		db_table = 'filters'

class Picked(models.Model):
	username = models.CharField(max_length=150, null=True, blank=True)
	property_url = models.CharField(max_length=200, null=True, blank=True)
	index = models.IntegerField(null=True, blank=True)
	was_picked = models.BooleanField(default=False)
	
	class Meta:
		db_table = 'picked'
