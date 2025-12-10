from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CreateUserForm
from properties.models import Property
from users.models import Customer

import datetime


def signup_page(request):
	context = {}
	
	form = CreateUserForm()
	
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			email = request.POST.get('email')
			password = request.POST.get('password1')
			
			if User.objects.filter(email=email).exists():
				messages.error(request, 'Username with this email alredy exists')
				
				context['form'] = form
				return render(request, 'pages/signup.html', context)
			
			user = User.objects.create_user(username=email, email=email)
			user.set_password(password)
			user.save()
			
			new_customer = Customer.objects.create(
				user=user,
				email=email
			)
			new_customer.save()
			
			messages.success(request, 'Your account was created Successfully')
			
			return redirect('login')
	
	context['form'] = form
	
	return render(request, 'pages/signup.html', context)

def login_page(request):
	if request.method == 'POST': 
		username = request.POST.get('username')
		password = request.POST.get('password')
		
		user = authenticate(request, username=username, password=password)
		
		if user is not None:
			login(request, user)
			
			return redirect('users:users-home')
		else:
			messages.info(request, 'Username or Password is incorrect')
			
	context = {}
	return render(request, 'pages/login.html', context)

def logout_page(request):
	logout(request)
	return redirect('login')

def landing_page(request):
	
	logged_in = request.user != "AnonymousUser"
	
	context = {
		"logged_in": logged_in
	}
	return render(request, 'pages/landing.html', context)
