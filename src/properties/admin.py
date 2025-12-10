from django.contrib import admin

from .models import (
	Property,
	Location,
)


admin.site.register(Property)
admin.site.register(Location)
