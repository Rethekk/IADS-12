from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('opportunity/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('accounts/profile/', views.profile, name='profile'),
    path('opportunity/<int:pk>/participate/', views.participate, name='participate'),
    path('about-us/', views.about_us, name='about_us'),
    path('termsOfService/', views.terms_of_service, name='terms_of_service'),
    path('volunteerCriteria/', views.volunteerCriteria, name='volunteerCriteria'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('careers/', views.careers, name='careers'),
    path('search_suggestions/', views.search_suggestions, name='search_suggestions'),
    path('register/organization/', views.register_organization, name='register_organization'),
    path('dashboard/organization/', views.organization_dashboard, name='organization_dashboard'),
    path('dashboard/organization/create-event/', views.CreateEventView.as_view(), name='create_event'),
    path('dashboard/organization/edit-event/<int:pk>/', views.EditEventView.as_view(), name='edit_event'),
    path('dashboard/organization/delete-event/<int:pk>/', views.DeleteEventView.as_view(), name='delete_event'),
    path('events/<int:event_id>/participants/', views.event_participants, name='event_participants'),

    path('login/organization/', views.organization_login, name='login_organization'),

    # password rest
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
