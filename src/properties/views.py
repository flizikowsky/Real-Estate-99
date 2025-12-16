import json

from django.shortcuts import redirect, render
from django.views import View
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Property
from users.models import (
	Customer,
	Filter
)
from .functions import conver_to_histogram_data

from datetime import datetime, timedelta
from numpy import sum


PROPERTIES_PER_PAGE = 5

@login_required(login_url='login')
def property_list_view(request):
	
	filters, property_list, query_string = filter_properties(request)
	saved_properties_url = [object_.url for object_ in Property.objects.filter(saved__email=request.user.username)]
	
	property_list = property_list.exclude(not_interested__email=request.user.username)
	
	if 'today' in request.path:
		picked_option = 'today'
		property_list = property_list.filter(date_added__gte=datetime.now().strftime('%Y-%m-%d'))
	elif 'month' in request.path:
		month_ago = datetime.strftime(datetime.now() - timedelta(30), '%Y-%m-%d')
		picked_option = 'month'
		property_list = property_list.filter(date_added__gte=month_ago)
	else:
		picked_option = 'all'
	
	prices = []
	surfaces = []
	for property_obj in property_list:
		if property_obj.price is not None:
			prices.append(property_obj.price)
		if property_obj.surface is not None:
			surfaces.append(property_obj.surface)
	
	prices.sort()
	if len(prices) > 4:
		prices_data = conver_to_histogram_data(prices)
		prices_data['mean'] = int(sum(prices) / len(prices))
		prices_data['median'] = prices[int(len(prices) / 2)]
		prices_data['p_per_m'] = int(sum(prices) / sum(surfaces))
	else:
		prices_data = "None"
	
	#	Pegination
	page = request.GET.get('page', 1)
	properties_paginator = Paginator(property_list, PROPERTIES_PER_PAGE)
	
	try:
		property_list = properties_paginator.page(page)
	except PageNotAnInteger:
		property_list = properties_paginator.page(1)
	except EmptyPage:
		property_list = properties_paginator.page(1)
	except page <= 0:
		property_list = properties_paginator.page(1)
		
	map_data = [{
		"name": f"{p.t_property} - {p.t_sell} in {p.location}",
		"address": p.location,
		"locationName": f"{p.t_property} - {p.t_sell} in {p.location}",
		"lat": p.longitude,
		"lng": p.latitude
	} for p in property_list]
	
	context = {
		'title': 'Property List',
		'description': 'Here is list of all properties on market, feel free to find your next investation',
		'object_list': property_list,
		'saved_object_list': saved_properties_url,
		'picked_option': picked_option,
		'filters': filters,
		'query_string': query_string,
		't_properties': ['dom', 'mieszkanie', 'dzialka'],
		't_sells': ['wynajem', 'sprzedaz'],
		'prices_data': prices_data,
		'map_data': json.dumps(map_data),
	}
	
	return render(request, 'properties/property_list.html', context)


@login_required(login_url='login')
def property_create_view(request):
	if request.method == 'POST':
		location = request.POST.get('location')
		price = request.POST.get('price')
		surface = request.POST.get('surface')
		type_estate = request.POST.get('type_estate')
		type_sell = request.POST.get('type_sell')
		print(request.POST)
		print(location)
		new_estate = Property.objects.create(
			url='http://127.0.0.1:8000',
			location=location,
			price=price,
			surface=surface,
			t_property=type_estate,
			t_sell=type_sell,
			date_added=datetime.now().strftime('%Y-%m-%d'),
			date_created=datetime.now().strftime('%Y-%m-%d'),
		)
		return redirect('users:users-home')
	
	return render(request, 'properties/property_create.html', {})


def filter_properties(request):

	queryset = Property.objects.all()
	filters = {}
	filter_query_string = ''
	
	for key in request.GET.keys():
		if key != 'page':
			filter_query_string += f'{key}={request.GET.get(key)}&'
	query_string = filter_query_string[0:(len(filter_query_string) - 1)]
	
	location = request.GET.get('l')
	min_price = request.GET.get('min_p')
	max_price = request.GET.get('max_p')
	min_surface = request.GET.get('min_s')
	max_surface = request.GET.get('max_s')
	t_property = request.GET.get('t_p')
	t_sell = request.GET.get('t_s')
	
	username = request.user.username
	if len(request.GET.keys()) == 0:
		filter_objects = Filter.objects.filter(username__exact=username)
		last_filter = filter_objects.last()
		
		if last_filter != None:
			location = last_filter.location
			min_price = last_filter.min_price
			max_price = last_filter.max_price
			min_surface = last_filter.min_surface
			max_surface = last_filter.max_surface
			t_property = last_filter.type_property
			t_sell = last_filter.type_sell
	
	customer = Customer.objects.get(email=username)
	new_filter = Filter(username=username)
	#	Location
	if location != '' and location != None:
		queryset = queryset.filter(location__icontains=location)
		filters['location'] = location
		new_filter.location = location
	
	#	Price
	if min_price != '' and min_price != None:
		queryset = queryset.filter(price__gte=min_price)
		filters['min_price'] = min_price
		new_filter.min_price = min_price
		
	if max_price != '' and max_price != None:
		queryset = queryset.filter(price__lte=max_price)
		filters['max_price'] = max_price
		new_filter.max_price = max_price
	
	#	Surface
	if min_surface != '' and min_surface != None:
		queryset = queryset.filter(surface__gte=min_surface)
		filters['min_surface'] = min_surface
		new_filter.min_surface = min_surface
		
	if max_surface != '' and max_surface != None:
		queryset = queryset.filter(surface__lte=max_surface)
		filters['max_surface'] = max_surface
		new_filter.max_surface = max_surface
	
	#	Type of Property
	if t_property != '' and t_property != None:
		queryset = queryset.filter(t_property__exact=t_property)
		
		filters['t_property'] = t_property
		new_filter.type_property = t_property
		customer.last_property_type = t_property
	#	Type of Sell
	if t_sell != '' and t_sell != None:
		queryset = queryset.filter(t_sell__exact=t_sell)
		customer.last_sell_type = t_sell
		filters['t_sell'] = t_sell
		new_filter.type_sell = t_sell
	
	if len(request.GET.keys()) != 0:
		if len(queryset) != 0:
			to_delete = Filter.objects.filter(username__exact=username)
			if to_delete != None:
				to_delete.delete()
			new_filter.save()
		customer.save()
	
	return filters, queryset, query_string
