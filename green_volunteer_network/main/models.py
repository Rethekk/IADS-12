from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    website = models.URLField(blank=True, null=True)
    contact_email = models.EmailField()

    def __str__(self):
        return self.name

class Initiative(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name

class Opportunity(models.Model):
    name = models.CharField(max_length=255)
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()
    volunteers_needed = models.IntegerField()

    def __str__(self):
        return self.name
