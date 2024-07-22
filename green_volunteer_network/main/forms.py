from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Contact, Organization, VolunteerOpportunity
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        label='Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label='Password'
    )
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_photo']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5}),
        }


class OrganizationRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=255, help_text='Enter organization name')
    description = forms.CharField(widget=forms.Textarea, help_text='Enter a brief description')
    website = forms.URLField(max_length=200, help_text='Enter your website URL')
    contact_email = forms.EmailField(help_text='Enter a contact email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'name', 'description', 'website', 'contact_email']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            organization = Organization(user=user, name=self.cleaned_data['name'], description=self.cleaned_data['description'],
                                        website=self.cleaned_data['website'], contact_email=self.cleaned_data['contact_email'])
            organization.save()
            profile = Profile.objects.create(user=user, is_organization=True)
        return user

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

class OrganizationLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organization Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def confirm_login_allowed(self, user):
        # You can add custom logic here to verify if the user is an organization
        super().confirm_login_allowed(user)
        if not user.is_organization:  # Assuming 'is_organization' is a user attribute to differentiate users
            raise forms.ValidationError("Login not allowed. Please make sure you are logging in as an organization.", code='invalid_login')



class CreateEventForm(forms.ModelForm):
    class Meta:
        model = VolunteerOpportunity
        fields = ['title', 'description', 'date', 'location', 'province', 'additional_info', 'image']  # Add 'province' here
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super(CreateEventForm, self).__init__(*args, **kwargs)
        self.fields['date'].input_formats = ('%Y-%m-%dT%H:%M',)