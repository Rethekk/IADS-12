from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from django.core.exceptions import ValidationError

class Organization(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organization')
    name = models.CharField(max_length=255)
    description = models.TextField()
    website = models.URLField(max_length=200, default='http://example.com')
    contact_email = models.EmailField()

    def __str__(self):
        return self.name

    @property
    def total_donations(self):
        return self.donations.aggregate(total=models.Sum('amount'))['total'] or 0

class VolunteerOpportunity(models.Model):
    PROVINCE_CHOICES = (
        ('AB', 'Alberta'),
        ('BC', 'British Columbia'),
        ('MB', 'Manitoba'),
        ('NB', 'New Brunswick'),
        ('NL', 'Newfoundland and Labrador'),
        ('NS', 'Nova Scotia'),
        ('ON', 'Ontario'),
        ('PE', 'Prince Edward Island'),
        ('QC', 'Quebec'),
        ('SK', 'Saskatchewan'),
        ('NT', 'Northwest Territories'),
        ('NU', 'Nunavut'),
        ('YT', 'Yukon'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    province = models.CharField(max_length=2, choices=PROVINCE_CHOICES, default='ON')
    additional_info = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='opportunity_images/', blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='participated_opportunities')

    def __str__(self):
        return self.title

class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='donations')
    donor_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.donor_name} - ${self.amount}'


class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(VolunteerOpportunity, on_delete=models.CASCADE)
    registered_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.opportunity.title}'



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_organization = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Quote(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=100)

    def __str__(self):
        return self.author


# class StaffMember(models.Model):
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='staff_members')
#     name = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=128)
#     confirm_password = models.CharField(max_length=128)
#
#     def clean(self):
#         if self.password != self.confirm_password:
#             raise ValidationError("Passwords do not match")
#
#     def __str__(self):
#         return self.name