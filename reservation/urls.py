from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import dashboard, request_lab,  reservation_schedule
from .forms import LoginForm

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('request/', request_lab, name='request_lab'),
    path('schedule/', views.reservation_schedule, name='reservation_schedule'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]
