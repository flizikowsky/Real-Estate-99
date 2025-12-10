def conver_to_histogram_data(objects):
	data = {}
	objects.sort()
	
	n = 20
	
	devide_number = int((objects[-4] - 0) / n)
	
	numbers_data = []
	i_numbers = 0
	prev_max = 0
	for i in range(len(objects)):
		if objects[i] > (prev_max + devide_number):
			numbers_data.append(i_numbers)
			i_numbers = 0
			prev_max += devide_number
		
		i_numbers += 1
	numbers_data.append(i_numbers)
	data['numbers_data'] = numbers_data
	
	m = (n / 4)
	label_number = int((objects[-4] - 0) / m)
	
	
	labels = []
	prev_label = 0
	for i in range(len(numbers_data)):
		if (i + 1) % m == 0:
			prev_label += label_number
			labels.append(str(prev_label))
		else:
			labels.append('')
	data['labels'] = labels
	
	return data
	
