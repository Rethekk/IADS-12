from django.contrib import admin
from .models import Organization, VolunteerOpportunity, Registration, Pledge, Profile

admin.site.register(Organization)
admin.site.register(VolunteerOpportunity)
admin.site.register(Registration)
admin.site.register(Pledge)
admin.site.register(Profile)

