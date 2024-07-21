from datetime import timezone
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .models import VolunteerOpportunity
from .forms import UserRegisterForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .forms import ProfileUpdateForm,ContactForm, UserUpdateForm
from .models import Profile
from django.shortcuts import render, redirect
from .forms import OrganizationRegistrationForm
from .models import Organization
from .forms import StaffMemberForm



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
    return render(request, 'main/opportunity_detail.html', {'opportunity': opportunity})

def participate(request, pk):
    opportunity = get_object_or_404(VolunteerOpportunity, pk=pk)
    if request.user not in opportunity.participants.all():
        opportunity.participants.add(request.user)
        messages.success(request, f'You have successfully registered for {opportunity.title}')
    else:
        messages.info(request, f'You are already registered for {opportunity.title}')
    return redirect('profile')

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
            form.save()
            return redirect('add_staff_member')
    else:
        form = OrganizationRegistrationForm()
    return render(request, 'main/register_organization.html', {'form': form})

def add_staff_member(request):
    if request.method == 'POST':
        form = StaffMemberForm(request.POST)
        if form.is_valid():
            staff_member = form.save(commit=False)
            # Assuming the organization is tied to the currently logged-in user
            staff_member.organization = request.user.organization
            staff_member.save()
            return redirect('add_staff_member')
    else:
        form = StaffMemberForm()
    return render(request, 'main/add_staff_member.html', {'form': form})