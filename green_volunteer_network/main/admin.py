from django.contrib import admin
from .models import Organization, VolunteerOpportunity, Registration, Donation, Contact, Profile

admin.site.register(Organization)
admin.site.register(VolunteerOpportunity)
admin.site.register(Registration)
admin.site.register(Donation)
admin.site.register(Profile)
admin.site.register(Contact)
