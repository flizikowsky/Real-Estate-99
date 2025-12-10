from django.contrib import admin

from .models import (
	Customer,
	Filter,
	Picked
)


admin.site.register(Customer)
admin.site.register(Filter)
admin.site.register(Picked)
