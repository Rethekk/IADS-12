from datetime import timezone

from django.contrib.auth import logout, login, authenticate
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

from .models import VolunteerOpportunity
from .forms import UserRegisterForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .forms import ProfileUpdateForm
from .models import Profile

def home(request):
    query = request.GET.get('q', '')
    opportunities = VolunteerOpportunity.objects.all()
    if query:
        # Split the query into individual words
        query_words = query.split()
        from django.db.models import Q
        filter_query = Q()
        for word in query_words:
            filter_query |= Q(title__icontains=word) | Q(description__icontains=word)
        opportunities = VolunteerOpportunity.objects.filter(filter_query)

    return render(request, 'main/home.html', {'opportunities': opportunities})

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
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if p_form.is_valid():
            print("Form is valid. Saving the profile photo.")
            p_form.save()
            return redirect('profile')  # Redirect to the same view after successful update
        else:
            print("Form is invalid.")
    else:
        p_form = ProfileUpdateForm(instance=user_profile)

    context = {
        'user_profile': user_profile,
        'p_form': p_form,
    }

    return render(request, 'main/profile.html', context)

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