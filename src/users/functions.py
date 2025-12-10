from properties.models import Property
from properties.models import Location
from .models import (
	Customer,
	Picked
)

import numpy
import math
from random import randrange
import json
from decimal import Decimal


def create_model(email):
	prices = []
	surfaces = []
	distances = []
	responses = []
	property_types = {
		'dom': 0,
		'mieszkanie': 0,
		'dzialka': 0
	}
	
	for obj in Property.objects.filter(saved__email=email):
		prices.append(obj.price)
		surfaces.append(obj.surface)
		
		obj_location = Location.objects.get(name__icontains=obj.location)
		distances.append(obj_location.distance_from_city)
		
		property_types[obj.t_property] += 1
		
		responses.append('yes')
	for obj in Property.objects.filter(not_interested__email=email):
		prices.append(obj.price)
		surfaces.append(obj.surface)
		
		obj_location = Location.objects.get(name__icontains=obj.location)
		distances.append(obj_location.distance_from_city)
		
		if obj.t_property != 'None':
			property_types[obj.t_property] += 1
		
		responses.append('no')
	if len(Property.objects.filter(not_interested__email=email)) == 0:
		prices.append(0)
		surfaces.append(0)
		distances.append(0)
	
	data = {}
	data['price'] = prices
	data['surface'] = surfaces
	data['distance_from_city'] = distances
	data['response'] = responses
	predict_property_type = sorted(property_types.items(), key=lambda x: x[1], reverse=True)[0][0]
	
	predict_key = 'response'
	processed_data = {}
	
	for key in data.keys():
		for value_num in range(len(data[key])):
			if not (key in processed_data):
				processed_data[key] = {}
			
			value = data[key][value_num]
			response = data[predict_key][value_num]
			if key == predict_key:
				if not (value in processed_data[predict_key]):
					processed_data[key][value] = 1.0
				else:
					processed_data[key][value] += 1

			else:
				if not (response in processed_data[key]):
					if not (type(value) is int):
						processed_data[key][response] = {}
					else:
						processed_data[key][response] = []

				if not (type(value) is int):
					if not (value in processed_data[key][response]):
						processed_data[key][response][value] = 0.0
					processed_data[key][response][value] += 1
				else:
					processed_data[key][response].append(value)
	
	for key in processed_data:
		if key != predict_key:
			for response in processed_data[predict_key]:
				for value_key in processed_data[key][response]:
					if not (type(processed_data[key][response]) is list):
						if not ('{}_probability'.format(response) in processed_data[key]):
							processed_data[key]['{}_probability'.format(response)] = {}
						processed_data[key]['{}_probability'.format(response)][value_key] = (
							processed_data[key][response][value_key] / processed_data[predict_key][response]
						)
					else:
						miu = float(numpy.sum(processed_data[key][response])) / len(processed_data[key][response])
						processed_data[key]['{}_miu'.format(response)] = miu

						sigma = math.sqrt(numpy.sum([((x - miu) ** 2) for x in processed_data[key][response]]) / 
							len(processed_data[key][response]))
						if sigma == 0 and key == 'price':
							sigma = 10000
						elif sigma == 0 and key == 'distance_from_city':
							sigma = 1
						elif sigma == 0 and key == 'surface':
							sigma = 10
						processed_data[key]['{}_sigma'.format(response)] = sigma
	
	processed_data['predict_property_type'] = predict_property_type
	
	file_name = ''
	customer = Customer.objects.get(email=email)
	if customer.model_name == '' or customer.model_name == None:
		file_name = random_string(15)
		customer.model_name = file_name
		customer.save()
	else:
		file_name = customer.model_name
	file = open(f'users_model/{file_name}.json', 'w')
	file.write(json.dumps(processed_data, ensure_ascii=False))
	file.close()

def pick_properties(email):
	customer = Customer.objects.get(email=email)
	file_name = customer.model_name
	processed_data = {}
	with open(f'users_model/{file_name}.json', 'r') as j:
		json_data = json.load(j)
		processed_data = json_data
	
	predict_property_type = processed_data['predict_property_type']
	objects_test = Property.objects.filter(
		t_property__exact=predict_property_type,
		t_sell__exact=Customer.objects.get(email=email).last_sell_type,
	).exclude(
		saved__email=email,
		not_interested__email=email,
	)
	predict_key = 'response'
	picked = {}
	
	for i in range(len(objects_test)):
		check_property = objects_test[i]
		
		was_picked = Picked.objects.filter(username__exact=email, property_url__exact=check_property.url)
		if was_picked:
			continue
		
		location_obj = Location.objects.filter(name__iexact=check_property.location)
		if not location_obj:
			continue
			
		data = {
			'distance_from_city': location_obj[0].distance_from_city,
			'price': check_property.price,
			'surface': check_property.surface,
		}
		if type(data['price']) is not int:
			continue
		
		value, picked_bool = use_model(processed_data, data, predict_key)
		if picked_bool:
			picked[objects_test[i].url] = value
	
	picked_sorted = [Property.objects.get(url=url) for url, v in sorted(picked.items(), key=lambda item: item[1])]
	i = 1
	for picked_obj in picked_sorted[:10]:
		new_picked = Picked.objects.create(username=email, property_url=picked_obj.url, index=i)
		new_picked.save()
		i += 1

def use_model(processed_data, data, predict_key):
	prior_probability = {}
	for response in processed_data[predict_key]:
		if not (response in prior_probability):
			prior_probability[response] = 0.0
	for response in prior_probability.keys():
		prior_probability[response] = processed_data[predict_key][response] / numpy.sum(
			[processed_data[predict_key][x] for x in prior_probability.keys()])

	likelihoods = {}
	for response in processed_data[predict_key]:
		if not (response in likelihoods):
			likelihoods[response] = 1.0
	for response in likelihoods.keys():
		for key in data.keys():
			if not (type(processed_data[key][response]) is list):
				for word in processed_data[key][response].keys():
					likelihood = processed_data[key]['{}_probability'.format(response)][word]
					likelihoods[response] *= likelihood
			else:
				miu = processed_data[key]['{}_miu'.format(response)]
				sigma = processed_data[key]['{}_sigma'.format(response)]
				if data[key] is None:
					continue
				likelihood = 1.0 / math.sqrt(2 * math.pi * sigma ** 2) * math.exp(-(data[key] - miu) ** 2 / sigma)
				likelihoods[response] *= likelihood

	normalization_constant = 1.0
	for key in data.keys():
		if type(processed_data[key]['yes']) is dict:
			normalization_constant *= (processed_data[key]['yes'][data[key]] + processed_data[key]['no'][
				data[key]]) / (processed_data[predict_key]['yes'] + processed_data[predict_key]['no'])
		else:
			normalization_constant *= (len(processed_data[key]['yes']) + len(processed_data[key]['no'])) / (
						processed_data[predict_key]['yes'] + processed_data[predict_key]['no'])

	posterior_probability = {}
	for response in processed_data[predict_key]:
		if not (response in posterior_probability):
			posterior_probability[response] = likelihoods[response] * prior_probability[
				response] / normalization_constant

	posterior_probability = sorted(posterior_probability.items(), key=lambda x: x[1], reverse=True)
	posterior_probability_yes = likelihoods['yes'] * prior_probability['yes'] / normalization_constant
	posterior_probability_no = likelihoods['no'] * prior_probability['no'] / normalization_constant
	
	if posterior_probability_yes == 0:
		return 0, False
	else:
		if posterior_probability[0][0] == 'yes':
			return posterior_probability_yes, True
		else:
			return 0, False

def random_string(max_number):
	letters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
	
	text = ""
	for _ in range(max_number):
		random = randrange(len(letters))
		text += letters[random]
	
	return text
