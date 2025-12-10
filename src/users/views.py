from django.http import HttpResponse
try:
	from django.utils import simplejson as json
except ImportError:
	import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import (
	Customer,
	Picked
)
from properties.models import Property
from .functions import (
	create_model,
	pick_properties
)

import datetime
import threading


@login_required(login_url='login')
def home_view(request):
	username = request.user.username
	boxes = [
		{
			'number': Property.objects.filter(saved__email=username).count,
			'text': 'Saved',
		},
	]
	user_picked = Picked.objects.filter(username__exact=username).exclude(was_picked=True).order_by('id')[:5]
	picked = [Property.objects.get(url=picked_obj.property_url) for picked_obj in user_picked]
	context = {
		'today_objects': Property.objects.filter(date_added__gte=datetime.datetime.now().strftime('%Y-%m-%d')).order_by('-id')[:10],
		'picked_objects': picked,
		'box_list': boxes,
	}
	return render(request, 'users/dashboard.html', context)
	
@login_required(login_url='login')
def saved_view(request):
	property_list = Property.objects.filter(saved__email=request.user.username)
	context = {
		'title': 'Saved',
		'description': 'Here are all your saved properties',
		'object_list': property_list,
		'saved_object_list': [obj.url for obj in property_list],
		
	}
	return render(request, 'properties/property_list.html', context)

@login_required
@require_POST
def save_property_view(request):
	if request.method == 'POST':
		email = request.user.username
		property_id = request.POST.get('id', None)
		
		property_obj = Property.objects.get(pk=property_id)
		customer_obj = Customer.objects.get(email=email)
		
		if Property.objects.filter(saved__email=email, url__icontains=property_obj.url).exists():
			property_obj.saved.remove(customer_obj)
		else:
			property_obj.saved.add(customer_obj)
		
		create_model(email)
		pick_thread = threading.Thread(target=pick_properties, args=[email])
		pick_thread.start()
	
	ctx = {}
	return HttpResponse(json.dumps(ctx), content_type='application/json')

@login_required
@require_POST
def not_interested_property_view(request):
	if request.method == 'POST':
		email = request.user.username
		property_id = request.POST.get('id', None)
		
		property_obj = Property.objects.get(pk=property_id)
		customer_obj = Customer.objects.get(email=email)
		
		property_obj.not_interested.add(customer_obj)
		
		create_model(email)
		pick_thread = threading.Thread(target=pick_properties, args=[email])
		pick_thread.start()

	ctx = {}
	return HttpResponse(json.dumps(ctx), content_type='application/json')

@login_required
@require_POST
def refresh_picked_view(request):
	if request.method == 'POST':
		username = request.user.username
		to_change_list = Picked.objects.filter(username__exact=username).exclude(was_picked=True).order_by('id')
		
		if to_change_list.count() <= 5:
			pick_thread = threading.Thread(target=pick_properties, args=[username])
			pick_thread.start()
		
		for to_change in to_change_list[:5]:
			
			to_change.was_picked = True
			to_change.save()
		
		new_picked = Picked.objects.filter(username__exact=username).exclude(was_picked=True).order_by('id')[:5]
		picked_list = [Property.objects.filter(url__exact=picked_object.property_url)[0] for picked_object in new_picked]
		picked_data = [
			{
				'surface': picked_obj.surface,
				'price': picked_obj.price,
				'location': picked_obj.location,
				't_property': picked_obj.t_property,
				'url': picked_obj.url,
				'id': picked_obj.id
			} for picked_obj in picked_list
		]
	ctx = {'picked_data_list': picked_data}
	return HttpResponse(json.dumps(ctx), content_type='application/json')
