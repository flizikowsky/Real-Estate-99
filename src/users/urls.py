from django.urls import path
from .views import (
	home_view,
	saved_view,
	save_property_view,
	not_interested_property_view,
	refresh_picked_view,
)

app_name = 'users'
urlpatterns = [
	path('', home_view, name='users-home'),
	path('saved', saved_view, name='users-saved'),
	path('like/', save_property_view, name='save'),
	path('dislike/', not_interested_property_view, name='not_interested'),
	path('refresh_picked/', refresh_picked_view, name='refresh_picked'),
]