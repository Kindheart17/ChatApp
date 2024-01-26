from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('', views.index, name='index'),
    path('logout/', views.logout_user, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.editProfile, name='edit'),
    path('image/', views.image, name='img'),
]