from django.db import models


class Property(models.Model):
	url = models.CharField(max_length=200)
	
	price = models.IntegerField(null=True, blank=True)
	surface = models.IntegerField(null=True, blank=True)
	location = models.CharField(max_length=50, null=True, blank=True)
	t_property = models.CharField(max_length=45, null=True, blank=True)
	t_sell = models.CharField(max_length=45, null=True, blank=True)
	
	s_plot = models.IntegerField(null=True, blank=True)
	t_plot = models.CharField(max_length=45, null=True, blank=True)
	n_rooms = models.IntegerField(null=True, blank=True)
	floor = models.IntegerField(null=True, blank=True)
	n_floors = models.IntegerField(null=True, blank=True)
	t_construction = models.CharField(max_length=45, null=True, blank=True)
	p_condition = models.CharField(max_length=45, null=True, blank=True)
	build_year = models.IntegerField(null=True, blank=True)
	market = models.CharField(max_length=45, null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)

	date_added = models.DateField(null=True)
	date_created = models.DateField(null=True)
	
	class Meta:
		db_table = 'estates'
	
	def __str__(self):
		return self.url
	
	def get_fields(self):
		people_keys = {
			'id': '',
			'url': '',
			
			'price': 'cena',
			'surface': 'powierzchnia',
			'location': 'lokalizacja',
			't_property': 'typ nieruchomosci',
			't_sell': 'typ sprzedarzy',
			
			's_plot': 'powierzchnia działki',
			't_plot': 'typ działki',
			'n_rooms': 'liczba pokoi',
			'floor': 'piętro',
			'n_floors': 'liczba pięter',
			't_construction': 'typ zabudowy',
			'p_condition': 'wykończenie',
			'build_year': 'rok budowy',
			'market': 'rynek',
			'longitude': 'longitude',
			'latitude': 'latitude',
			'date_added': '',
			'date_created': ''
		}
		
		return [(people_keys[f'{field.name}'], field.value_to_string(self)) for field in Property._meta.fields]


class Location(models.Model):
	name = models.CharField(max_length=30)
	location_type = models.CharField(max_length=45, null=True, blank=True)
	distance_from_city = models.IntegerField(null=True, blank=True)
	distance_city_name = models.CharField(max_length=30, null=True, blank=True)
	
	class Meta:
		db_table = 'locations'
