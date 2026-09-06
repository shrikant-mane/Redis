from django.urls import path

from accounts.views import (
    RegisterView,
    LoginView,
    ProfileView,
    BookView,
    LogoutView,
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('books/', BookView.as_view(), name='books'),
    path('logout/', LogoutView.as_view(), name='logout'),
]