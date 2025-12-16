from django.urls import path
from .views import (
	property_list_view,
	property_create_view
)

app_name = 'properties'
urlpatterns = [
	path('', property_list_view, name='properties-list'),
	path('month', property_list_view, name='properties-list-month'),
	path('today', property_list_view, name='properties-list-today'),
	path('create', property_create_view, name='properties-create'),
]
