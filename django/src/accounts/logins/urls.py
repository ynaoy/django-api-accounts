from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

app_name = "logins"

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/', views.IndexView.as_view(), name='index'),
    path('api/signup/', views.SignupView.as_view(), name='signup'),
    path('api/update/<int:pk>', views.UpdateView.as_view(), name='update'),
    path('api/update_password/<int:pk>', views.UpdatePasswordView.as_view(), name='update_password'),
    path('api/login', views.LoginView.as_view(), name='login'),
    path('api/logout', views.LogoutView.as_view(), name='logout'),
]