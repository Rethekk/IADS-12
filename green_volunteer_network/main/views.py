from datetime import timezone
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .models import VolunteerOpportunity, Organization
from .forms import UserRegisterForm, OrganizationRegistrationForm, OrganizationLoginForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from .forms import ProfileUpdateForm,ContactForm, UserUpdateForm
from .models import Profile
from .forms import CreateEventForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django import forms
import datetime
from django.db import IntegrityError

def home(request):

    #Session Counting
    today = datetime.date.today()
    if 'has_visited' not in request.session:
        total_visits = request.session.get('total_visits', 0) + 1
        request.session['total_visits'] = total_visits
        request.session['has_visited'] = True
        request.session.set_expiry(0)

    #Search
    query = request.GET.get('q', '')
    province = request.GET.get('province', '')
    opportunities = VolunteerOpportunity.objects.all()
    if query:
        opportunities = opportunities.filter(title__icontains=query)
    if province:
        opportunities = opportunities.filter(province=province)

    total_visits = request.session.get('total_visits', 0)

    return render(request, 'main/home.html', {
        'opportunities': opportunities,
        'PROVINCE_CHOICES': VolunteerOpportunity.PROVINCE_CHOICES,
        'total_visits': total_visits
    })

def search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = list(VolunteerOpportunity.objects.filter(title__icontains=query).values_list('title', flat=True)[:10])
    return JsonResponse({'suggestions': suggestions})

def search_view(request):
    query = request.GET.get('q', '')
    opportunities = VolunteerOpportunity.objects.filter(title__icontains=query) | VolunteerOpportunity.objects.filter(description__icontains=query)
    return render(request, 'main/home.html', {'opportunities': opportunities})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = UserRegisterForm()
    return render(request, 'main/register.html', {'form': form})

@login_required
def profile(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')  # Redirect to the same view after successful update
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=user_profile)

    participated_opportunities = request.user.participated_opportunities.all()

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'participated_opportunities': participated_opportunities,
        'user_profile': user_profile,
    }

    return render(request, 'main/profile.html', context)

# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#         if user:
#             if user.is_active:
#                 login(request, user)
#                 request.session['last_login'] = str(timezone.now())
#                 request.session.set_expiry(60)
#                 return HttpResponseRedirect(reverse('home'))
#             else:
#                 return HttpResponse('Your account is disabled.')
#         else:
#             return HttpResponse('Invalid login details.')
#     else:
#         return render(request, 'registration/login.html')
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    request.session['last_login'] = str(timezone.now())
                    request.session.set_expiry(60)
                    return redirect(reverse('home'))
                else:
                    return HttpResponse('Your account is disabled.')
            else:
                return HttpResponse('Invalid login details.')
        else:
            return render(request, 'registration/login.html', {'form': form})
    else:
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


def opportunity_detail(request, pk):
    opportunity = get_object_or_404(VolunteerOpportunity, pk=pk)
    already_participating = request.user in opportunity.participants.all()

    if request.method == "POST" and request.user.is_authenticated:
        if not already_participating:
            opportunity.participants.add(request.user)
            # Instead of redirect, we use JsonResponse to notify the client-side
            return JsonResponse({'status': 'success', 'message': 'You have successfully registered!'})
        else:
            return JsonResponse({'status': 'already_registered', 'message': 'You are already registered!'})

    return render(request, 'main/opportunity_detail.html', {
        'opportunity': opportunity,
        'already_participating': already_participating
    })

def participate(request, pk):
    opportunity = get_object_or_404(VolunteerOpportunity, pk=pk)
    if request.user not in opportunity.participants.all():
        opportunity.participants.add(request.user)
        messages.success(request, f'You have successfully registered for {opportunity.title}')
    else:
        messages.info(request, 'You are already registered for this event.')
    return redirect('opportunity_detail', pk=pk)

def about_us(request):
    return render(request, 'main/aboutUs.html')

def terms_of_service(request):
    return render(request, 'main/termsOfService.html')

def volunteerCriteria(request):
    return render(request, 'main/volunteerCriteria.html')

def careers(request):
    return render(request, 'main/careers.html')

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact_us')
    else:
        form = ContactForm()
    return render(request, 'main/contact_us.html', {'form': form})




def register_organization(request):
    if request.method == 'POST':
        form = OrganizationRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # Create organization
            organization = Organization(
                user=user,
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                website=form.cleaned_data['website'],
                contact_email=form.cleaned_data['contact_email']
            )
            organization.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.is_organization = True
            profile.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome to Green Volunteer Network!')
            logout(request)
            return HttpResponseRedirect(reverse('home'))
            # return redirect('organization_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = OrganizationRegistrationForm()
    return render(request, 'registration/register_organization.html', {'form': form})


@login_required
def organization_dashboard(request):
    if not request.user.profile.is_organization:
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('home')
    return render(request, 'main/organization_dashboard.html')


def organization_login(request):
    if request.method == 'POST':
        form = OrganizationLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('organization_dashboard')  # Redirect to the organization's dashboard
            else:
                return render(request, 'registration/login_organization.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = OrganizationLoginForm()
    return render(request, 'registration/login_organization.html', {'form': form})


class CreateEventView(CreateView):
    model = VolunteerOpportunity
    form_class = CreateEventForm
    template_name = 'main/create_event.html'
    success_url = reverse_lazy('organization_dashboard')  # Redirect to the organization dashboard after success

    def form_valid(self, form):
        form.instance.organization = self.request.user.organization
        return super().form_valid(form)

class EditEventView(UpdateView):
    model = VolunteerOpportunity
    fields = ['title', 'description', 'date', 'location', 'province', 'additional_info', 'image']
    template_name = 'main/edit_event.html'
    success_url = reverse_lazy('organization_dashboard')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].widget = forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
        form.fields['date'].input_formats = ('%Y-%m-%dT%H:%M',)
        return form

class DeleteEventView(DeleteView):
    model = VolunteerOpportunity
    template_name = 'main/delete_event.html'
    success_url = reverse_lazy('organization_dashboard')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "The event has been deleted.")
        return super().delete(request, *args, **kwargs)

@login_required
def event_participants(request, event_id):
    event = get_object_or_404(VolunteerOpportunity, pk=event_id)
    # Check if the logged-in user is associated with the organization
    if request.user.organization != event.organization:
        return redirect('some_error_page')  # or handle it by showing a message

    participants = event.participants.all()
    return render(request, 'main/event_participants.html', {'event': event, 'participants': participants})