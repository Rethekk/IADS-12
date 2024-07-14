from django.contrib import admin
from .models import Organization, Initiative, Opportunity

admin.site.register(Organization)
admin.site.register(Initiative)
admin.site.register(Opportunity)
